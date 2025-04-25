#!/bin/sh

docker build -t registry.swarm.internal/bksi-be:gateway -f gateway/Dockerfile .
docker build -t registry.swarm.internal/bksi-be:report -f report/Dockerfile .
docker build -t registry.swarm.internal/bksi-be:management -f management/Dockerfile .
docker build -t registry.swarm.internal/bksi-be:ticket -f ticket/Dockerfile .
docker build -t registry.swarm.internal/bksi-be:dashboard -f dashboard/Dockerfile .
docker build -t registry.swarm.internal/bksi-be:healthcheck -f healthcheck/Dockerfile .
