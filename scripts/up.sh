#!/usr/bin/env bash
# Builds the whole platform from zero: cluster + monitoring (Terraform), then deploys the app.
set -euo pipefail
cd "$(dirname "$0")/.."

cd terraform
terraform init -input=false
terraform apply -auto-approve -input=false

cd .. && ./scripts/deploy.sh "${1:-local}"

echo
echo "Ready:"
echo "  App        http://localhost:8080"
echo "  Grafana    http://localhost:3000   (admin / secureship) -> dashboard 'SecureShip - DevBoard'"
echo "  Prometheus http://localhost:9090"
echo "  Alerts     http://localhost:9093"
