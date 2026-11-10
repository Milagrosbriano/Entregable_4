# Dos proyectos independientes
- gestor-gastos-backend: FastAPI, SQLite, métricas, Dockerfile, Kubernetes y monitoreo.
- gestor-gastos-frontend: interfaz existente, configuración de API, Nginx, Dockerfile y Kubernetes propios.

Podés mover cada carpeta a un repositorio diferente. Ningún proyecto importa archivos del otro; se comunican por HTTP. Seguí el README de cada carpeta. Para desarrollo local iniciar primero backend en 8000 y después frontend en 8080. Para Docker o Minikube iniciar primero backend, después frontend. Se conservan ambas interfaces: index.html (v2) y v1.html.

La separación no completa por sí sola el Laboratorio 4. No se agregaron Jenkins, Helm ni nuevas evidencias de escaneo. Docker/Kubernetes deben validarse en tu equipo; no están disponibles en el entorno de preparación.
