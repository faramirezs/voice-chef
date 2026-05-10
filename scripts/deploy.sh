#!/bin/bash

mkdir -p /goinfre/$(whoami)/.docker_data
mkdir -p /goinfre/$(whoami)/.config/docker
cat > /goinfre/$(whoami)/.config/docker/daemon.json << 'EOF'
{
  "data-root": "/goinfre/<intra_name>/.docker_data",
  "registry-mirrors": ["https://nexus.42berlin.de:5000"]
}
EOF
systemctl --user restart docker
sleep 2 && docker info | grep "Docker Root Dir"
df -h /goinfre/$(whoami)/.docker_data
git clone git@github.com:faramirezs/voice-chef.git /goinfre/$(whoami)/voice-chef
