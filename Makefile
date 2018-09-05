

all:	package repo

repo:	docs/index.yaml

docs/index.yaml:	docs/*.tgz
	helm repo index docs --merge docs/index.yaml

package:
	rm -rf tmp && mkdir -p tmp
	helm package . -d tmp
	mv -nv tmp/* docs/
	rm -rf tmp

templates/scripts.yaml:	src/sync-pods
	kubectl create configmap auto-updater-scripts \
    	--from-file $< \
    	--dry-run -o yaml > $@

.PHONY: clean package repo all
