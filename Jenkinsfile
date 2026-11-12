
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

        stage('Verificar Docker') {
            steps {
                echo 'Comprobando la conexión con Docker...'
                sh 'docker version'
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
