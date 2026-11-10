# Analisis de imagenes Docker

## Resultados

| Componente | Imagen | Tamano local | Capas | Usuario | Eficiencia Dive | Espacio desperdiciado |
|---|---|---|---|---|---|---|
| Backend | gestor-gastos-backend:v1 | 56,47 MiB | 9 | 10001:10001 | 97,6657 % | 5.697.355 bytes |
| Frontend | gestor-gastos-frontend:v1 | 24,77 MiB | 10 | 101:101 | 99,3682 % | 636.756 bytes |

Los tamanos corresponden al valor Size informado por docker image inspect.
No representan necesariamente el tamano comprimido de descarga del registry.
La cantidad de capas corresponde a RootFS.Layers.

## Contenerizacion

Cada componente tiene su propio Dockerfile y utiliza multi-stage builds.
El backend prepara las dependencias en una etapa separada.
El frontend valida y prepara sus archivos con Node; la imagen final utiliza Nginx.

Ambas imagenes declaran usuarios distintos de root.
Se utilizan etiquetas de version explicitas, sin latest.

## Analisis de capas con Dive

Ambas imagenes obtuvieron PASS con la configuracion predeterminada de CI.
Pasaron las reglas highestUserWastedPercent y lowestEfficiency.
La regla highestWastedBytes estaba deshabilitada y no fue evaluada.

### Backend

El mayor desperdicio observado corresponde a versiones repetidas de archivos
de debconf y dpkg, junto con registros del sistema.

Como oportunidad de mejora se propone revisar las capas de la imagen base
y comparar futuras versiones compatibles de python:3.12-slim.
Eliminar archivos heredados en una capa posterior no recupera el espacio
que ya ocupan en las capas anteriores.

### Frontend

El desperdicio observado corresponde principalmente al certificado de CA,
metadatos de apk y archivos de Nginx sobrescritos por la configuracion propia.

La eficiencia obtenida es alta. Como mejora futura se puede evaluar otra
imagen base compatible y comparar su tamano y mantenimiento, conservando
los certificados necesarios y la ejecucion sin privilegios.

## Escaneo de vulnerabilidades con Trivy

Pendiente de incorporar los resultados de:
- trivy-backend.txt
- trivy-frontend.txt

No se afirma ausencia de vulnerabilidades hasta revisar ambos reportes.

## Evidencias

- image-summary.txt
- dive-backend.txt
- dive-frontend.txt
- trivy-backend.txt
- trivy-frontend.txt

## Correccion de vulnerabilidades del frontend

El escaneo inicial detecto 273 hallazgos, incluidos 3 criticos.
La actualizacion general de paquetes redujo el resultado a 7 hallazgos,
todos correspondientes a Nginx.

Se identifico que Nginx estaba fijado a la version 1.28.3-r1.
Se eliminaron modulos adicionales no utilizados por la aplicacion
y se actualizo Nginx a 1.28.3-r7.

El escaneo posterior con Trivy detecto 0 vulnerabilidades.
Este resultado corresponde a la imagen y a la base de vulnerabilidades
utilizadas en ese momento.

La configuracion de Nginx paso la validacion nginx -t.
Los tamanos y resultados anteriores del frontend son historicos;
las medidas actualizadas estan en image-summary.txt y dive-frontend.txt.
