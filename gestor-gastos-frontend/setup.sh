#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
minikube status >/dev/null 2>&1 || minikube start
docker build -t gestor-gastos-frontend:v1 .
minikube image load gestor-gastos-frontend:v1
kubectl apply -f k8s/ --recursive=false
kubectl rollout status deployment/gestor-gastos-frontend --timeout=180s
