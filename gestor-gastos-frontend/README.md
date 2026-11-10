# Gestor de gastos — Frontend
Proyecto HTML, CSS y JavaScript independiente. Mantiene el diseño oscuro, registro de gastos, tabla, total y gráfico por categoría de v2. `v1.html` conserva la interfaz sin gráfico como alternativa. No necesita npm, compilación ni archivos del backend.

## Ejecución local
Desde esta carpeta, con Python instalado:
```powershell
python -m http.server 8080
```
Abrir http://localhost:8080; para v1, http://localhost:8080/v1.html.
Ejecutar la API por separado en el puerto 8000 siguiendo su propio README.
`config.js` define la URL de la API (incluyendo `/api`). Si se cambia el dominio o puerto de la interfaz, autorizarlo también en CORS_ORIGINS del backend. Abrir mediante HTTP, no con doble clic sobre el HTML.

## Docker
Primero iniciar el contenedor backend en la red gastos-net según su README. Desde esta carpeta:
```powershell
docker build -t gestor-gastos-frontend:v1 .
docker run --rm --name gestor-gastos-frontend --network gastos-net -p 8080:8080 gestor-gastos-frontend:v1
```
Abrir http://localhost:8080. La imagen usa Nginx sin root y reemplaza config.js por config.docker.js para usar `/api` en el mismo origen. Nginx reenvía las peticiones a `gestor-gastos-backend:8000` conservando `/api`; si cambia el nombre del servicio o contenedor, ajustar nginx.conf y reconstruir.

## Kubernetes / Minikube
Primero desplegar backend en el mismo cluster y namespace default. Luego, desde esta carpeta:
```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
minikube service gestor-gastos-frontend
```
En Bash: `bash setup.sh`. Este proyecto solo construye y despliega el frontend; se conecta al Service independiente gestor-gastos-backend.

## Limpieza
```powershell
kubectl delete -f k8s/
```
Cada proyecto puede colocarse en su propio repositorio. Los scripts de cambio blue/green del proyecto anterior no aplican a esta separación. Esta entrega separa los proyectos; no incorpora todos los requisitos adicionales del Laboratorio 4.
