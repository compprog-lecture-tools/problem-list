# Problem list builder image

This directory contains a docker image that can be used to built the problem list, for example in a CI job.
It contains all the necessary build tools preinstalled, except for the python libraries (which can be cached in a CI job).

Since it should rarely change, it is not being built automatically.
If you change anything here, be sure to rebuild it with
```shell script
docker build -t hpiicpc/problem-list-builder:latest .
```
and then upload it using
```shell script
docker push hpiicpc/problem-list-builder:latest
```

