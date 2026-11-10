$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
minikube status
if ($LASTEXITCODE -ne 0) { minikube start; if ($LASTEXITCODE -ne 0) { throw "No se pudo iniciar minikube" } }
docker build -t gestor-gastos-backend:v1 .
if ($LASTEXITCODE -ne 0) { throw "Falló Docker build" }
minikube image load gestor-gastos-backend:v1
if ($LASTEXITCODE -ne 0) { throw "Falló la carga de la imagen" }
kubectl apply -f k8s/
if ($LASTEXITCODE -ne 0) { throw "Falló kubectl apply" }
kubectl rollout status deployment/gestor-gastos-backend --timeout=180s
if ($LASTEXITCODE -ne 0) { throw "El deployment no está listo" }
