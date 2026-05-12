# Local Single-Node Deployment

Running the full stack on one machine. Suitable for personal use, home servers,
or development machines that are not behind a VPN. If your machine is on
Tailscale or another VPN, see [Deployment on VPN](vpn-deployment.md) instead —
pod networking behaves differently.

---

## 1 — Install k3s

```bash
curl -sfL https://get.k3s.io | sh -

sudo chmod 644 /etc/rancher/k3s/k3s.yaml
```

## 2 — GPU setup (only if using `llamacpp.enabled: true`)

Skip this step if you are using an external model backend (cloud API, or a
llamacpp service running outside the cluster). Kubernetes does not need to know
about the GPU in those cases.

If you are running the in-cluster llamacpp deployment, k3s uses its own bundled
containerd (not the system Docker daemon), so the NVIDIA runtime must be
configured for both:

```bash
sudo nvidia-ctk runtime configure --runtime=containerd
sudo systemctl restart containerd

sudo nvidia-ctk runtime configure --runtime=containerd \
  --config=/var/lib/rancher/k3s/agent/etc/containerd/config.toml
sudo systemctl restart k3s
```

Deploy the NVIDIA device plugin so Kubernetes can schedule GPU workloads:

```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.17.0/deployments/static/nvidia-device-plugin.yml

# Verify — should output "1" after ~30 s
kubectl get nodes -o json | jq '.items[].status.capacity["nvidia.com/gpu"]'
```

## 3 — Install Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## 4 — Install the chart

```bash
helm install ai-assistant oci://registry-1.docker.io/sinanozel/ai-assistant-helm \
  --version 0.1.0 \
  -f my-values.yaml \
  --namespace ai-assistant \
  --create-namespace
```

Minimum `my-values.yaml` for an external llamacpp backend:

```yaml
llamacpp:
  enabled: false

cortex:
  hostPath: /home/youruser/.config/ai-assistant/cortex
```

## 5 — Connect to an external llamacpp backend

If llamacpp is running as a Docker/systemd service on the same host (port 8080),
expose it to the cluster with a Kubernetes Service and Endpoints object.

Get the node's internal IP — this is the address pods use to reach the host:

```bash
kubectl get nodes -o wide --no-headers | awk '{print $6}'
```

Save as `llamacpp-host.yaml` and apply it:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: llamacpp-host
  namespace: ai-assistant     # match your release namespace
spec:
  ports:
    - port: 8080
      targetPort: 8080
---
apiVersion: v1
kind: Endpoints
metadata:
  name: llamacpp-host
  namespace: ai-assistant     # match your release namespace
subsets:
  - addresses:
      - ip: 192.168.x.x      # node INTERNAL-IP from above
    ports:
      - port: 8080
```

```bash
kubectl apply -f llamacpp-host.yaml
```

In your cortex `providers/default.yaml`:

```yaml
api_base: http://llamacpp-host:8080/v1
model: openai/gemma4-e2b
api_key: dummy
timeout: 300
```

The node's internal IP is stable as long as the machine is on the same network.
If it changes (e.g. DHCP reassignment), update the Endpoints object and
re-apply — no other configuration changes are needed.

## 6 — Expose the service

The chart creates a ClusterIP service (cluster-internal only). Apply a
LoadBalancer service so k3s's built-in klipper binds it to the node's real
network interfaces:

Save as `ai-assistant-lb.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-assistant-external
  namespace: ai-assistant
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: ai-assistant-helm
    app.kubernetes.io/instance: ai-assistant
    app.kubernetes.io/component: app
  ports:
    - name: http
      port: 8000
      targetPort: 8000
    - name: streamlit
      port: 8501
      targetPort: 8501
```

```bash
kubectl apply -f ai-assistant-lb.yaml
```

## 7 — Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000/tcp    # AI assistant API
sudo ufw allow 8501/tcp    # Streamlit UI
sudo ufw enable
```
