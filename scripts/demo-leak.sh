#!/usr/bin/env bash
# Demo A bonus: pushes a branch with a (randomly generated, fake) AWS secret key.
# Gate 1 (gitleaks) must fail on it. The key is created at runtime so it never lives in the repo.
set -euo pipefail
cd "$(dirname "$0")/.."
KEY=$(python -c "import secrets, string; a = string.ascii_letters + string.digits; print(''.join(secrets.choice(a) for _ in range(40)))")
git checkout -b demo/leak-$(date +%H%M%S)
echo "AWS_SECRET_ACCESS_KEY = \"$KEY\"" > app/config.py
git add app/config.py
git commit -m "Add config"
git push -u origin HEAD
gh pr create --title "Add config" --body "demo: gitleaks should block this"
git checkout main
