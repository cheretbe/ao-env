```shell
cd /ao-env
docker build . --build-arg base_image=ubuntu:18.04 --tag test-image:1.0 -f tests/docker/Dockerfile

docker run -dt --name test test-image:1.0 /bin/sh
docker run -dt --name test -v `pwd`:/ao-env test-image:1.0 /bin/sh

docker exec -ti test /bin/bash

py.test -v tests/unit_tests
py.test --hosts='docker://test' -v tests/installer_tests

docker rm test --force
```