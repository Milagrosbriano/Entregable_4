# Gestor de gastos — Backend
Proyecto FastAPI independiente, sin archivos del frontend. Conserva SQLite, los endpoints y la instrumentación Prometheus originales. La API era idéntica en v1 y v2, por eso hay un solo backend.

## Windows / PowerShell (Python 3.12)
Desde esta carpeta:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```
En Linux/macOS usar `.venv/bin/python` y `.venv/bin/python -m uvicorn main:app --reload --port 8000`.

- Swagger: http://localhost:8000/docs
- Estado: GET /healthz
- Categorías: GET /api/categorias
- Gastos: GET /api/gastos y POST /api/gastos
- Métricas: GET /metrics
- El backend ya no sirve una página en `/`; devuelve 404 allí.

Ejemplo JSON para POST /api/gastos:
```json
{"descripcion":"Almuerzo","monto":250,"categoria":"Comida"}
```
`DB_PATH` define el archivo SQLite; por defecto es `data/gastos.db` dentro de este proyecto. `CORS_ORIGINS` acepta una lista separada por comas; por defecto localhost:8080 y 127.0.0.1:8080. Para otro frontend, configurá su origen antes de iniciar la API. El ZIP original no contenía una base de datos cargada.

## Docker
```powershell
docker network create gastos-net
docker build -t gestor-gastos-backend:v1 .
docker run --rm --name gestor-gastos-backend --network gastos-net -p 8000:8000 -v gastos-data:/app/data gestor-gastos-backend:v1
```
Crear la red una sola vez. El volumen conserva los datos al recrear el contenedor. La imagen usa multi-stage y usuario 10001.

## Kubernetes / Minikube
Usar el contexto minikube y namespace default, con su StorageClass predeterminada habilitada.
```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
kubectl port-forward service/gestor-gastos-backend 8000:8000
```
En Bash: `bash setup.sh`. Hay un PVC de 1 GiB. Se usa una réplica y estrategia Recreate por SQLite. Los manifiestos usan imagePullPolicy Never para imágenes cargadas con minikube.

## Monitoreo existente
Con backend desplegado:
```powershell
powershell -ExecutionPolicy Bypass -File setup-monitoring.ps1
minikube service grafana
minikube service prometheus
```
En Bash: `bash setup-monitoring.sh`. Se conservaron las configuraciones del entregable anterior; Prometheus descubre pods con app=gestor-gastos-backend. Grafana usa las credenciales originales de laboratorio admin/admin. El dashboard conserva RPS, latencia, gastos por categoría y memoria de proceso. No equivale a tener completo el Laboratorio 4.

## Limpieza
```powershell
kubectl delete -f k8s/monitoring/
kubectl delete deployment gestor-gastos-backend
kubectl delete service gestor-gastos-backend
```
Se conserva el PVC. `kubectl delete pvc gestor-gastos-data` elimina el almacenamiento y sus gastos.

## Pruebas
```powershell
.\.venv\Scripts\python.exe -m pip install pytest httpx
.\.venv\Scripts\python.exe -m pytest -q
```
Los informes DOCX en docs son históricos; los comandos vigentes son los de este README. La estrategia blue/green anterior no se conserva como despliegue activo: ahora se despliegan backend y frontend por separado.
