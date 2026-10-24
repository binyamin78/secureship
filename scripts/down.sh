#!/usr/bin/env bash
# Deletes everything (the kind cluster and all it contains).
set -euo pipefail
cd "$(dirname "$0")/../terraform"
terraform destroy -auto-approve
