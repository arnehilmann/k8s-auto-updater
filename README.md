# k8s-auto-updater

auto-update your cluster: sync your docker images and restart pods running on outdated images

**!!! DO NOT USE IN A PRODUCTION ENVIRONMENT !!!**

*bad things could happen: service downtime, permanent pod restarts, hailstorms, ... You have been warned!*

find the current chart index at
[https://arnehilmann.github.io/k8s-auto-updater/index.yaml](https://arnehilmann.github.io/k8s-auto-updater/index.yaml)

## Description

**in your cluster**
`k8s-auto-updater` runs as a cronjob inside your kubernetes-cluster.

**with the authority**
`k8s-auto-updater` uses the commands `docker` and `kubectl`, has
access to the docker socket (and thus full access to the docker daemon of the corresponding node),
is allowed to list, get, and delete pods and to get secrets (per RBAC definition).

**gathering image names**
`k8s-auto-updater` fetches all image names used by the pods in its namespace.

**syncing images**
Then it pulls all images, updating the local docker registry if the image in the remote registry has changed.

**deleting pods**
Then `k8s-auto-updater` iterates over all pods (again), checking if the image id the pod was started on equals
the image id referenced by the image name. If the image id of the pod differs, the pod gets deleted and
(hopefully; assuming a ha-setup) a new pod gets created using the newly pulled image.


## tl;dr

```
helm install --name auto-updater https://arnehilmann.github.io/k8s-auto-updater/k8s-auto-updater-0.0.4.tgz
# cross fingers
```


## setup

A more permanent setup would be to add this repo to your helm installation and install `k8s-auto-updater` from there:

```
helm repo add k8s-a-u-chart https://arnehilmann.github.io/k8s-auto-updater/
helm install --name auto-updater k8s-a-u-chart/k8s-auto-updater
```


## config

The following parameters could be set via `--set`:

parameter | default | description
--------- | ------- | -----------
schedule | \*/10 \* \* \* \* | when to run `k8s-auto-updater`, uses [cron syntax](https://en.wikipedia.org/wiki/Cron#Overview)
suspend  | false             | should `k8s-auto-updater` run on startup or stay in suspend mode

**example:**
```
helm install --name auto-updater k8s-a-u-chart/k8s-auto-updater --set schedule="*/2 * * * *"  # run every two minutes
```


## cleanup

```
helm delete auto-updater
```


## TODO

- [ ] allow selector for pod selection
- [x] allow image sync for remote registries which do not need PullSecrets
- [ ] provide endpoint for triggering manually
