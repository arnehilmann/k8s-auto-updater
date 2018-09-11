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


def rolling_update_on_deployment(pod, pod_name, repodigest, **args):
    '''
    strategy for check_pods
    '''
    print(args.keys())

    replica_set = get_first_owner(pod)
    if not replica_set:
        print("\tno owning replica set found for pod/{}, strange!".format(pod_name))
        return False

    deployment = get_first_owner(replica_set)
    if not deployment:
        print("\tno owning deployment found for replicaset/{}, strange!".format(
            replica_set["metadata"]["name"]))
        return False

    print("\tsetting newestrepodigst to {} in deployment/{}".format(
        repodigest, deployment["metadata"]["name"]))
    raw_result = subprocess.run([
        "kubectl", "set", "env",
        "deployment/{}".format(deployment["metadata"]["name"]),
        "newestrepodigest={}".format(repodigest)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if raw_result.returncode != 0:
        print("\t[WARN] {}".format(raw_result.stderr))
        return False

    return True


def run():
    '''
    actually run the check with the rolling_update_on_deployment strategy
    '''
    header("auto-updater", "=")
    print(".\nsyncing pods and images against local and remote registry\n")

    image_regexp = os.getenv("IMAGE_REGEXP", ".*")
    pod_selectors = os.getenv("POD_SELECTOR", "auto-update=enabled")

    header("fetching pods, current repodigest and image name")
    print("\timage regexp: {}".format(image_regexp))
    print("\tpod selectors: {}".format(pod_selectors))

    data = collect_data(image_regexp, pod_selectors)

    header("checking remote repositories, deleting outdated pods")
    check_pods(data, rolling_update_on_deployment)

    print(".\ndone.")
