# Parte 5 — Seguridad integrada (DevSecOps)

En esta parte se revisa la seguridad del proyecto en cuatro momentos:

- Semgrep revisa el código buscando errores de seguridad.
- Snyk revisa las librerías que usa el backend buscando versiones con fallas conocidas.
- Kyverno controla que solo se puedan crear en Kubernetes pods configurados de forma segura.
- Falco vigila lo que pasa dentro de los contenedores mientras corren y avisa si ve algo sospechoso.

Todos los comandos se ejecutan en la terminal, parado en la carpeta del repositorio (Entregable_4). Todos los resultados se guardan en la carpeta reports/.

# Requisitos 

- Docker Desktop abierto
- minikube, kubectl y Helm instalados
- Una cuenta gratuita en snyk.io

Antes de empezar, se ejecuta este comando para que los reportes se guarden con los caracteres correctos:

    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# Estructura
En semgrep/reglas-seguridad.yaml están las dos reglas propias de Semgrep; en kyverno/politicas/ las 4 políticas de Kyverno; en kyverno/pruebas/ los pods de prueba para comprobar las políticas

# 5.1 Semgrep

Semgrep lee el código sin ejecutarlo y busca patrones peligrosos. Usamos dos reglas propias:

- Una para el backend, que busca consultas SQL armadas pegando texto del usuario. Eso permitiría que alguien modifique la consulta (SQL injection).
- Una para el frontend, que busca datos del usuario insertados como HTML en la página. Eso permitiría que alguien inserte código que se ejecute en el navegador (XSS).

Además se usan las reglas oficiales de seguridad de Semgrep para Python y JavaScript.

Se ejecuta el siguiente comando:

    docker run --rm -v "${PWD}:/src" -w /src semgrep/semgrep semgrep scan --metrics=off --config seguridad/semgrep/reglas-seguridad.yaml --config p/python --config p/javascript gestor-gastos-backend gestor-gastos-frontend 2>&1 | Tee-Object -FilePath reports\semgrep-report.txt

El resultado queda en reports/semgrep-report.txt.

Resultado obtenido: se revisaron 4 archivos con 221 reglas y no se encontró ningún problema. Esto es porque el backend arma las consultas SQL con parámetros (?) y el frontend muestra los datos como texto (textContent) y no como HTML.

# 5.2 Snyk

Snyk compara las librerías del requirements.txt contra una base de vulnerabilidades conocidas.
1. Se ingresa a snyk.io, luego a Account settings y se copia tu Auth Token.

2. Se guarda el token en la terminal (reemplazando TOKEN):

        $env:SNYK_TOKEN = "TOKEN"

3. Se ejecuta el escaneo:

        docker run --rm --entrypoint sh -e SNYK_TOKEN -v "${PWD}\gestor-gastos-backend:/app" -w /app snyk/snyk:python-3.12 -c "pip install -q -r requirements.txt && snyk test --file=requirements.txt --package-manager=pip" 2>&1 | Tee-Object -FilePath reports\snyk-report.txt

El resultado queda en reports/snyk-report.txt.

Resultado obtenido: el primer escaneo (guardado en reports/snyk-report-antes.txt) encontró 8 vulnerabilidades: 5 altas y 3 medias. Todas estaban en la librería starlette, que no la usamos directamente sino que la trae FastAPI por dentro.

Para corregirlo se actualizó requirements.txt a fastapi 0.162.4 y starlette 1.10.0. Se comprobó que la aplicación sigue funcionando y se volvió a escanear: 0 vulnerabilidades.

# 5.3 Kyverno

Kyverno revisa cada pod antes de que Kubernetes lo cree. Si el pod no cumple una política, lo rechaza.

Se crearon 4 políticas, que aplican solo al namespace gestor-gastos (donde está la aplicación):

- prohibir-latest: la imagen tiene que tener una versión concreta, no latest.
- exigir-recursos: cada contenedor tiene que indicar cuánta CPU y memoria usa como mínimo y como máximo.
- impedir-root: los contenedores no pueden correr como administrador (root).
- impedir-escalada-privilegios: un proceso no puede conseguir más permisos de los que tiene al arrancar.

1. Se levanta el clúster:

        minikube start -p devsecops

2. Se instala Kyverno:

        helm repo add kyverno https://kyverno.github.io/kyverno/
        helm repo update
        helm install kyverno kyverno/kyverno -n kyverno --create-namespace --wait

3. Se cargan las políticas:

        kubectl apply -f seguridad\kyverno\politicas\

4. Se cargan las imágenes en el clúster y se desplega la aplicación:

        minikube -p devsecops image load gestor-gastos-backend:v1
        minikube -p devsecops image load gestor-gastos-frontend:v1
        kubectl create namespace gestor-gastos
        kubectl apply -n gestor-gastos -f gestor-gastos-backend\k8s\
        kubectl apply -n gestor-gastos -f gestor-gastos-frontend\k8s\

5. Se prueba crear un pod que rompe cada política, y uno que cumple todas:

        kubectl apply -f seguridad\kyverno\pruebas\prueba-latest.yaml
        kubectl apply -f seguridad\kyverno\pruebas\prueba-sin-recursos.yaml
        kubectl apply -f seguridad\kyverno\pruebas\prueba-root.yaml
        kubectl apply -f seguridad\kyverno\pruebas\prueba-escalada.yaml
        kubectl apply -f seguridad\kyverno\pruebas\prueba-valida.yaml

La salida de estos comandos está guardada en reports/kyverno-validation.log.

Resultado obtenido: los 4 pods que rompen una política fueron rechazados, cada uno con el mensaje de su política. El pod válido y los pods de la aplicación se crearon y funcionan.

# 5.4 Falco

Falco observa lo que hacen los procesos dentro de los contenedores y genera una alerta si algo coincide con un comportamiento sospechoso.

1. Se instala Falco:

        helm repo add falcosecurity https://falcosecurity.github.io/charts
        helm repo update
        helm install falco falcosecurity/falco -n falco --create-namespace --set driver.kind=modern_ebpf --set tty=true --wait

2. Se simula un ataque: se busca claves privadas SSH dentro del backend, como haría alguien que entró a la aplicación y quiere robar credenciales:

        kubectl exec -n gestor-gastos deploy/gestor-gastos-backend -- find / -name id_rsa

3. Se busca la alerta en los registros de Falco y se guarda:

        kubectl logs -n falco -l app.kubernetes.io/name=falco -c falco --tail 200 | Select-String "private keys" | Tee-Object -FilePath reports\falco-event.log

Resultado obtenido: Falco generó la alerta "Search Private Keys or Passwords". La alerta indica qué comando se ejecutó, con qué usuario (10001, que no es root), en qué imagen, en qué pod y en qué namespace. Además, la búsqueda no pudo entrar a carpetas protegidas como /root, porque el contenedor no corre como administrador.