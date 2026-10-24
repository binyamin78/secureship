#!/usr/bin/env bash
# Deploys DevBoard to the cluster.
#   ./scripts/deploy.sh            -> build the image locally and load it into kind
#   ./scripts/deploy.sh <git-sha>  -> deploy the image that passed the CI pipeline (from GHCR)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd -W 2>/dev/null || pwd)" # pwd -W = Windows path when running in Git Bash
export KUBECONFIG="$ROOT/terraform/kubeconfig"
CLUSTER="secureship"
GHCR_IMAGE="${GHCR_IMAGE:-ghcr.io/binyamin78/secureship-devboard}"
TARGET="${1:-local}"

if [[ "$TARGET" == "local" ]]; then
  IMAGE="secureship/devboard:local-$(date +%H%M%S)"
  echo ">> Building $IMAGE"
  docker build -t "$IMAGE" --build-arg APP_VERSION=local app
  kind load docker-image "$IMAGE" --name "$CLUSTER"
else
  IMAGE="$GHCR_IMAGE:$TARGET"
  echo ">> Deploying CI-approved image $IMAGE"
fi

kubectl kustomize k8s \
  | sed "s#image: secureship/devboard:local#image: $IMAGE#" \
  | kubectl apply -f -

kubectl -n secureship rollout status deployment/devboard --timeout=180s
kubectl -n secureship get pods -o wide
