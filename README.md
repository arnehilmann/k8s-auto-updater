# k8s-auto-updater

auto-update your cluster: sync your docker images and restart pods running on old images

*DO NOT USE IN A PRODUCTIVE ENVIRONMENT*

*bad things could happen: downtime, service outage, permanent pod restarts, hail storms, ...*

*You have been warned!*


## Description

*in your cluster*
`k8s-auto-updater` runs as a cronjob inside your kubernetes-cluster.

*gathering pods*
It searches for pods in its namespace, extracting both
the image name the pod is using, and
the image id the pod was started on.

*syncing images*
Then it pull all images, updating the local docker registry if the image in the remote registry has changed

*deleting pods*
Now the `k8s-auto-updater` iterates over all pods again, checking if the image id the pod was started on equals
the image id referenced by the image name. If the image id of the pod differs, the pod gets deleted and a
new pod gets created (hopefully) using the new image.


## tl;dr

```
helm install --name auto-updater https://arnehilmann.github.io/k8s-auto-updater/k8s-auto-updater-0.0.2.tgz
# cross fingers
```


## setup

A more permanent solution would be to add this repo to your helm installation and install `k8s-auto-updater` from there.

```
helm repo add k8s-a-u-chart https://arnehilmann.github.io/k8s-auto-updater/
helm install --name auto-updater k8s-a-u-chart/k8s-auto-updater
```


## cleanup

```
helm delete auto-updater
```

