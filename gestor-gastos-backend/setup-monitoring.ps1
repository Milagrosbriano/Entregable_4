$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
kubectl apply -f k8s/monitoring/
if ($LASTEXITCODE -ne 0) { throw "Falló el despliegue del monitoreo" }
foreach ($name in @("prometheus", "grafana")) {
    kubectl rollout status deployment/$name --timeout=180s
    if ($LASTEXITCODE -ne 0) { throw "No inició $name" }
}
