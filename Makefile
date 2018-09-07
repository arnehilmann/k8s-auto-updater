

all:	chart image

chart:	package repo

repo:	docs/index.yaml

docs/index.yaml:	docs/*.tgz
	helm repo index docs --merge docs/index.yaml

package:	templates/scripts.yaml
	rm -rf tmp && mkdir -p tmp
	helm package . -d tmp
	mv -nv tmp/* docs/
	rm -rf tmp

templates/scripts.yaml:	src/sync-pods
	kubectl create configmap auto-updater-scripts \
    	--from-file $< \
    	--dry-run -o yaml > $@

image:	docker/
	docker build -t arne/kubectlskopeo:latest docker
	docker push arne/kubectlskopeo:latest

.PHONY: package repo all image
