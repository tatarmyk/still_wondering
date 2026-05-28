#!/bin/bash
# Deploy script — run on the Oracle VM
# Usage: ssh user@server 'bash -s' < deploy.sh

set -e

APP_DIR="/opt/still_wondering"
REPO_URL="YOUR_GIT_REPO_URL_HERE"

echo "==> Pulling latest code..."
cd "$APP_DIR"
git pull origin main

echo "==> Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "==> Restarting service..."
sudo systemctl restart essays

echo "==> Done. Status:"
sudo systemctl status essays --no-pager -l
