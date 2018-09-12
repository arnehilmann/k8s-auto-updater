import base64
import json
import re
import subprocess

from kubepy import api as kubectl


def header(text, style="-", min_length=60):
    print(".")
    print(style * max(min_length, len(text)))
    print(text)
    print(style * max(min_length, len(text)))


def get_first_owner(resource):
    owners = resource["metadata"].get("ownerReferences", [])
    if not owners:
        return None
    return kubectl.get(owners[0]["kind"], owners[0]["name"])


def matches_pod(selectors, labels, name):
    selected = True
    for selector in selectors.split(","):
        if not selected:
            break
        if "!=" in selector:
            key, value = selector.split("!=")
            if labels.get(key) == value:
                selected = False
        elif "==" in selector:
            key, value = selector.split("==")
            if labels.get(key) != value:
                selected = False
        elif "=" in selector:
            key, value = selector.split("=")
            if labels.get(key) != value:
                selected = False
        else:
            key = selector
            if key and key not in labels:
                selected = False
        if not selected:
            print("skipped: pod/{} not selected because unmet criteria '{}'".format(name, selector))
    return selected


def fetch_credentials(digest2pods):
    creds = ""
    for _, pods in digest2pods.items():
        if creds:
            break
        for pod in pods:
            if creds:
                break
            pull_secrets = pod["spec"].get("imagePullSecrets", "null")
            if pull_secrets != "null":
                for pull_secret in pull_secrets:
                    token_name = pull_secret["name"]
                    token = kubectl.get("secret", token_name)
                    secret_base64 = token["data"].get(".dockerconfigjson", "")
                    if not secret_base64:
                        continue
                    secret_dict = json.loads(base64.b64decode(secret_base64))
                    hostname = list(secret_dict["auths"].keys())[0]
                    username = secret_dict["auths"][hostname]["username"]
                    password = secret_dict["auths"][hostname]["password"]
                    creds = "{}:{}".format(username, password)
                    break
    return creds


def split_image_name(image_name):
    host = namespace = repo = tag = ""
    repo, tag = image_name.rsplit(":", 1)
    if "/" in repo:
        namespace, repo = repo.rsplit("/", 1)
    if "/" in namespace:
        host, namespace = namespace.rsplit("/", 1)
    return host, namespace, repo, tag


def matches_image(regexp, name):
    if not re.match(regexp, name):
        # print("skipped: docker-image/{} skipped because missed regexp '{}'".format(name, regexp))
        return False
    return True


def collect_data(image_regexp, pod_selectors):
    image2digest2pods = {}
    for pod in kubectl.get("pods")["items"]:
        image_name = pod["status"]["containerStatuses"][0]["image"]

        if not matches_image(image_regexp, image_name):
            continue
        if not matches_pod(pod_selectors,
                           pod["metadata"].get("labels", {}),
                           pod["metadata"]["name"]):
            continue

        digest = re.sub("^.*@", "", pod["status"]["containerStatuses"][0].get("imageID", ""))
        if image_name not in image2digest2pods:
            image2digest2pods[image_name] = {}
        if digest not in image2digest2pods[image_name]:
            image2digest2pods[image_name][digest] = []
        image2digest2pods[image_name][digest].append(pod)

    for image in image2digest2pods:
        print("selected: docker-image/{}".format(image))

    return image2digest2pods


def query_repodigst(host, namespace, repo, tag, creds):
    raw_result = subprocess.run(
        filter(None,
               ["skopeo",
                "inspect",
                "--creds={}".format(creds) if creds else None,
                "docker://{}/{}/{}:{}".format(
                    host if host else "docker.io",
                    namespace if namespace else "library",
                    repo,
                    tag
                )]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if raw_result.returncode != 0:
        print("\t[WARN] {}".format(raw_result.stderr))
        return None
    result = json.loads(raw_result.stdout)
    return result["Digest"]


def check_pods(image2digest2pods, strategy):
    for image_name in image2digest2pods:
        print()
        print(image_name)

        host, namespace, repo, tag = split_image_name(image_name)
        creds = fetch_credentials(image2digest2pods[image_name])

        repodigest = query_repodigst(host, namespace, repo, tag, creds)
        if not repodigest:
            continue
        for pod in image2digest2pods[image_name].get(repodigest, []):
            print("\tuptodate: pod/{}".format(pod["metadata"]["name"]))
        for digest in image2digest2pods.get(image_name, {}):
            if digest == repodigest:
                continue
            for pod in image2digest2pods[image_name][digest]:
                pod_name = pod["metadata"]["name"]
                print("\toutdated: pod/{}".format(pod_name))
                print("\t\trepodigest of pod: {}".format(digest))
                print("\t\tnewest repodigest: {}".format(repodigest))

                if not strategy(**locals()):
                    print("\t[WARN] something went wrong...")
