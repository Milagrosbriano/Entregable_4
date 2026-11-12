
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
