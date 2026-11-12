
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Descargando el proyecto desde GitHub...'
                checkout scm
            }
        }

        stage('Validar Helm') {
            steps {
                echo 'Validando la Helm Chart...'
                sh 'helm lint ./helm-chart -f ./helm-chart/values-dev.yaml'
                sh 'helm template gastos ./helm-chart -f ./helm-chart/values-dev.yaml > /dev/null'
            }
        }
        stage('Tests') {
            steps {
                echo 'Ejecutando pruebas automaticas del backend...'
                sh 'docker build --progress=plain -f ./gestor-gastos-backend/Dockerfile.test -t gestor-gastos-tests .'
            }
        }
        stage('Semgrep') {
            steps {
                echo 'Analizando el codigo con Semgrep...'

                sh 'docker build --progress=plain -f Dockerfile.semgrep -t gestor-gastos-semgrep .'
            }
        }
        stage('Snyk') {
            steps {
                echo 'Analizando dependencias del backend con Snyk...'

                withCredentials([
                    string(
                        credentialsId: 'snyk-token',
                        variable: 'SNYK_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        set -eu

                        tar -C gestor-gastos-backend -cf - requirements.txt | \
                        docker run --rm -i \
                            -e SNYK_TOKEN \
                            --entrypoint /bin/sh \
                            snyk/snyk:python \
                            -c 'mkdir -p /app &&
                                tar -xf - -C /app &&
                                cd /app &&
                                snyk test --file=requirements.txt --severity-threshold=critical'
                    '''
                }
            }
        }
        stage('Verificar Docker') {
            steps {
                echo 'Comprobando la conexión con Docker...'
                sh 'docker version'
            }
        }
        stage('Build Docker') {
            steps {
                echo 'Construyendo imagen Docker del backend...'
                sh 'docker build -t gestor-gastos-backend:ci-${BUILD_NUMBER} ./gestor-gastos-backend'

                echo 'Construyendo imagen Docker del frontend...'
                sh 'docker build -t gestor-gastos-frontend:ci-${BUILD_NUMBER} ./gestor-gastos-frontend'

                echo 'Verificando las imagenes construidas...'
                sh 'docker image inspect gestor-gastos-backend:ci-${BUILD_NUMBER} > /dev/null'
                sh 'docker image inspect gestor-gastos-frontend:ci-${BUILD_NUMBER} > /dev/null'
            }
        }
        stage('Push Docker') {
            steps {
                echo 'Publicando imagenes en Docker Hub...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-jenkins',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        set -eu

                        export DOCKER_CONFIG="$(mktemp -d)"
                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT

                        printf '%s' "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        docker tag gestor-gastos-backend:ci-${BUILD_NUMBER} \
                            "$DOCKERHUB_USER/gestor-gastos-backend:ci-${BUILD_NUMBER}"

                        docker tag gestor-gastos-frontend:ci-${BUILD_NUMBER} \
                            "$DOCKERHUB_USER/gestor-gastos-frontend:ci-${BUILD_NUMBER}"

                        docker push "$DOCKERHUB_USER/gestor-gastos-backend:ci-${BUILD_NUMBER}"
                        docker push "$DOCKERHUB_USER/gestor-gastos-frontend:ci-${BUILD_NUMBER}"
                    '''
                }
            }
        }
        stage('Verificar Kubernetes') {
            steps {
                echo 'Comprobando el acceso a Minikube...'

                withCredentials([
                    file(
                        credentialsId: 'gastos-helm-kubeconfig',
                        variable: 'KUBECONFIG'
                    )
                ]) {
                    sh 'kubectl get pods -n gastos-helm'
                }
            }
        }
        stage('Deploy Helm') {
            steps {
                echo 'Desplegando las nuevas imagenes en Minikube...'

                withCredentials([
                    file(
                        credentialsId: 'gastos-helm-kubeconfig',
                        variable: 'KUBECONFIG'
                    ),
                    usernamePassword(
                        credentialsId: 'dockerhub-jenkins',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu

                        helm upgrade --install gastos ./helm-chart \
                            --namespace gastos-helm \
                            -f ./helm-chart/values-dev.yaml \
                            --set-string backend.image.repository="$DOCKERHUB_USER/gestor-gastos-backend" \
                            --set-string backend.image.tag="ci-$BUILD_NUMBER" \
                            --set backend.image.pullPolicy=IfNotPresent \
                            --set-string frontend.image.repository="$DOCKERHUB_USER/gestor-gastos-frontend" \
                            --set-string frontend.image.tag="ci-$BUILD_NUMBER" \
                            --set frontend.image.pullPolicy=IfNotPresent \
                            --wait \
                            --timeout 5m

                        kubectl rollout status deployment/gestor-gastos-backend -n gastos-helm --timeout=180s
                        kubectl rollout status deployment/gestor-gastos-frontend -n gastos-helm --timeout=180s

                        kubectl get pods -n gastos-helm
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Verificaciones iniciales completadas correctamente.'
        }
        failure {
            echo 'El pipeline falló. Revisar los logs de Jenkins.'
        }
    }
}
