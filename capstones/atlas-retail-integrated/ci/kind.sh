#!/usr/bin/env bash
# Disposable Kind integration. Creates and DELETES a fresh kind cluster.
# Must not run on a real Kubernetes context or a machine with valuable workloads.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
cluster="atlas-ci-$$"
cleanup() {
  kill "${forward_pid:-}" 2>/dev/null || true
  kind delete cluster --name "$cluster" || true
}
trap cleanup EXIT

kind create cluster --name "$cluster" --wait 90s
docker build -t atlas-retail-integrated:dev .
kind load docker-image atlas-retail-integrated:dev --name "$cluster"
kubectl apply -f k8s/stack.yaml
kubectl -n atlas-lab rollout status deployment/postgres --timeout=160s
kubectl -n atlas-lab rollout status deployment/objectstore --timeout=160s
kubectl -n atlas-lab wait --for=condition=complete job/atlas-seed --timeout=160s
kubectl -n atlas-lab rollout status deployment/atlas-api --timeout=160s
kubectl -n atlas-lab get endpoints atlas-api
kubectl -n atlas-lab get endpoints atlas-api -o jsonpath='{.subsets[0].addresses[0].ip}' | grep -E '[0-9]'

kubectl -n atlas-lab port-forward service/atlas-api 18083:8080 > /tmp/atlas-portforward.log 2>&1 &
forward_pid=$!
python ci/smoke_http.py

echo "Injecting unresolvable API image; old Ready replica must continue serving..."
kubectl -n atlas-lab set image deployment/atlas-api api=atlas-retail-integrated:unavailable
if kubectl -n atlas-lab rollout status deployment/atlas-api --timeout=35s; then
  echo "ERROR: deliberately broken image unexpectedly rolled out"
  exit 1
fi
python ci/smoke_http.py

echo "Rolling back broken image and verifying data-plane recovery..."
kubectl -n atlas-lab rollout undo deployment/atlas-api
kubectl -n atlas-lab rollout status deployment/atlas-api --timeout=120s
python ci/smoke_http.py
echo "PASS: integrated API Kubernetes readiness, private service, failed rollout and rollback"
