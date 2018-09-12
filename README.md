# k8s-auto-updater

auto-update your cluster: sync your docker images and restart pods running on outdated images

**!!! DO NOT USE IN A PRODUCTION ENVIRONMENT !!!**

*bad things could happen: service downtime, permanent pod restarts, hailstorms, ... You have been warned!*


## tl;dr

```
helm install --name auto-updater \
    https://arnehilmann.github.io/k8s-auto-updater/k8s-auto-updater-0.1.1.tgz \
    --set podSelector=
# cross fingers
```


## description

**in your cluster**
`k8s-auto-updater` runs as a cronjob inside your kubernetes-cluster.

**with the authority**
`k8s-auto-updater` uses [`skopeo`](https://github.com/containers/skopeo) and `kubectl`, and
has the following permissions:

resource    | verb
----------- | ----
pods        | list, get
secrets     | get
replicasets | get
deployments | get, **patch**

**gathering image names and its digests**
`k8s-auto-updater` fetches all pods and corresponding image names:
1) image name must match `imageRegExp` (default: `.*`, see #Notes)
2) pod labels must match `podSelector` (default: `auto-update=enabled`, see #Notes).

**deleting pods**
Then `k8s-auto-updater` iterates over selected pods, checking if the image id the pod was started on equals
the image id referenced by the image name. If the image id of the pod differs, the
owning replicaset and deployment get identified and then the deployment env gets patched, resulting
in a new replicaset and thus newly started pods.


## setup

A more permanent setup would be to add this repo to your helm installation and
install `k8s-auto-updater` from there (see the config part for customization):

```
helm repo add k8s-a-u-chart https://arnehilmann.github.io/k8s-auto-updater/
helm install --name auto-updater k8s-a-u-chart/k8s-auto-updater
```


## config

The following parameters could be set via `--set`:

parameter             | default             | description
--------------------- | ------------------- | -----------
schedule              | \*/10 \* \* \* \*   | when to run `k8s-auto-updater`, uses [cron syntax](https://en.wikipedia.org/wiki/Cron#Overview)
suspend               | false               | should `k8s-auto-updater` run on startup or stay in suspend mode
activeDeadlineSeconds | 300                 | hard timeout for the job
podSelector           | auto-update=enabled | select pods based on labels; supports '=', '!='
imageRegExp           | .\*                 | regular expression for matching docker images
verbose               | false               | produce more detailed log output

**example:**
```
helm install --name auto-updater \
    k8s-a-u-chart/k8s-auto-updater \
    --set schedule="*/2 * * * *" \  # run every two minutes
    --set podSelector=  # select _all_ pods in current namespace
```


## notes

* Clearing the `podSelector` variable might be a bad idea
(i.e. **all** pods, including system pods and auto-updater itself, get selected)!
* You can narrow the searched repositories by setting `imageRegExp`;
you can use multiple patterns with the `pattern1|pattern2` notation; e.g.
`... --set imageRegExp='arne/d.*|gitlab.*'`.
* when referencing images on `docker.io`, the host part of the image name is empty
(e.g. `arne/k8s-auto-updater` instead of `docker.io/arne/k8s-auto-updater`).
* when referencing official images on `docker.io`, the host and repo parts are empty
(e.g. `mysql` instead of `docker.io/library/mysql`).


## cleanup

```
helm delete auto-updater
```


## quick links

find the current chart index at
[https://arnehilmann.github.io/k8s-auto-updater/index.yaml](https://arnehilmann.github.io/k8s-auto-updater/index.yaml)

find the docker image at
[https://hub.docker.com/r/arne/kubectlskopeo/](https://hub.docker.com/r/arne/kubectlskopeo/)


## TODO

- [x] allow selector for pods, images, registries
- [x] specify how many pods per run may be deleted
- [x] allow image sync for remote registries which do not need PullSecrets
- [ ] provide endpoint for triggering manually (still in scope?)
- [x] only delete pod when image pull enabled (imageTag eq latest or imagePullPolicy Always)
