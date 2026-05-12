# Deployment on VPN (Tailscale)

Single-node deployment where the machine is on a Tailscale network. The setup
is mostly the same as [local deployment](local-deployment.md), but pod
networking introduces two problems that require specific workarounds when the
model backend runs outside the cluster on the same host.

---

## Networking concerns

k3s pods run in their own network namespace, isolated from the host's interfaces
by the Flannel overlay network. This causes two problems specific to Tailscale:

**DNS.** Tailscale MagicDNS uses a virtual resolver at `100.100.100.100`. This
address is only reachable via the Tailscale interface (`tailscale0`) on the
host. CoreDNS runs as a pod and cannot reach `100.100.100.100`, so Tailscale
hostnames (`<machine>.<tailnet>.ts.net`) fail to resolve from inside the
cluster.

**Routing.** Tailscale assigns IPs in the `100.64.0.0/10` range. Pod traffic
destined for those addresses goes through the host's routing table to
`tailscale0`, but Tailscale drops packets that do not originate from an
authenticated peer — pod IPs (`10.42.x.x`) are not peers.

An ExternalName service pointing to a Tailscale hostname fails for both reasons:
DNS resolution fails before a connection is even attempted.

---

## Steps 1–4: same as local deployment

Follow steps 1–4 from [local deployment](local-deployment.md) (k3s, GPU if
needed, Helm, chart install).

---

## 5 — Connect to an external llamacpp backend

Because pod networking cannot reach Tailscale addresses, the solution is to
run the pod in the host's network namespace. This gives the pod direct access
to all host interfaces including `tailscale0`, so Tailscale DNS works and
connections to the Tailscale IP are handled as local loopback.

After `helm install` or `helm upgrade`, patch the deployment:

```bash
kubectl patch deployment <release>-ai-assistant-helm \
  -n <namespace> \
  --type=json \
  -p='[
    {"op":"add","path":"/spec/template/spec/hostNetwork","value":true},
    {"op":"add","path":"/spec/template/spec/dnsPolicy","value":"ClusterFirstWithHostNet"}
  ]'
```

With `hostNetwork: true` in effect, use the Tailscale hostname directly in
your cortex `providers/default.yaml` — no llamacpp-host service needed:

```yaml
api_base: http://<machine>.<tailnet>.ts.net:8080/v1
model: openai/gemma4-e2b
api_key: dummy
timeout: 300
```

The Tailscale hostname is stable across IP reassignments and reboots. Because
the pod runs in the host's network namespace, the connection is a local loopback
— it never leaves the machine.

Note: the patch is overwritten on the next `helm upgrade`. Re-apply it after
every upgrade.

---

## 6 — Expose the service on Tailscale

Apply a LoadBalancer service. k3s's built-in klipper binds it to all node
interfaces, including the Tailscale interface, so the service is reachable at
the machine's Tailscale hostname:

Save as `ai-assistant-lb.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-assistant-external
  namespace: <your-namespace>
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: ai-assistant-helm
    app.kubernetes.io/instance: <your-release-name>
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

The agent is then reachable at:
- `http://<machine>.<tailnet>.ts.net:8000` — REST API
- `http://<machine>.<tailnet>.ts.net:8501` — Streamlit UI

## 7 — Firewall

Allow traffic from Tailscale peers only:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 41641/udp          # Tailscale WireGuard
sudo ufw allow in on tailscale0   # all traffic from Tailscale peers
sudo ufw enable
```
