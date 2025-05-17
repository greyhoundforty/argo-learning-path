
## k3d

```shell
k3d cluster create argo-cluster \
  --api-port 6443 \
  --port "80:80@loadbalancer" \
  --port "443:443@loadbalancer" \
  --agents 2
```