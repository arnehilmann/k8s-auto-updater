#!/usr/bin/env python
'''
trigger a rolling update on deployments when pods run on outdated images
'''

import os
import subprocess

from . import (header,
               collect_data,
               get_first_owner,
               check_pods)


def rolling_update_on_deployment(pod, pod_name, repodigest, patched={}, verbose=False, **args):
    '''
    strategy for check_pods
    '''
    # print(args.keys())

    replica_set = get_first_owner(pod)
    if not replica_set:
        print("\t\tno owning replica set found for pod/{}, strange!".format(pod_name))
        return False

    deployment = get_first_owner(replica_set)
    if not deployment:
        print("\t\tno owning deployment found for replicaset/{}, strange!".format(
            replica_set["metadata"]["name"]))
        return False

    print("\tsetting newestrepodigst to {} in deployment/{}".format(
        repodigest, deployment["metadata"]["name"]))
    raw_result = subprocess.run([
        "kubectl", "set", "env",
        "deployment/{}".format(deployment_name),
        "newestrepodigest={}".format(repodigest)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if raw_result.returncode != 0:
        print("\t\t[WARN] {}".format(raw_result.stderr))
        return False

    return True


def run():
    '''
    actually run the check with the rolling_update_on_deployment strategy
    '''
    header("k8s-auto-updater", "=")
    print("\nsyncing pods and images against local and remote registry")
    print("(see https://github.com/arnehilmann/k8s-auto-updater)\n")

    image_regexp = os.getenv("IMAGE_REGEXP", ".*")
    pod_selectors = os.getenv("POD_SELECTOR", "auto-update=enabled")
    verbose = str(os.getenv("VERBOSE", "")).lower() in ("true", "yes", "1")

    header("fetching pods, current repodigest and image name")
    print("IMAGE_REGEXP: {}".format(image_regexp))
    print("POD_SELECTOR: {}".format(pod_selectors))
    print("     VERBOSE: {}".format(verbose))

    data = collect_data(image_regexp, pod_selectors, verbose)

    header("checking remote repositories, patching deployments of outdated pods")
    check_pods(data, rolling_update_on_deployment, verbose)

    print("\ndone.")
