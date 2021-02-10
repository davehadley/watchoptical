pipeline {
    agent any
    // options {
    //     skipDefaultCheckout true
    // }
    stages {
        // stage('Clean') {
        //     steps {
        //         echo 'Clean'
        //         cleanWs()
        //         checkout scm
        //     }
        // }
        stage('Setup') {
            steps {
                echo 'Setup'
                sh '''#!/usr/bin/env bash
                    source setup-environment.sh 
                    '''
                
            }
        }
        stage('Build') {
            steps {
                sh '''#!/usr/bin/env bash
                source setup-environment.sh
                python build.py
                '''
            }
        }
        stage('Test Environment') {
            steps {
                echo 'Test Environment'
                sh '''#!/usr/bin/env bash
                source setup-environment.sh
                python test-environment.py
                '''
            }
        }
        stage('Integration Tests') {
            steps {
                echo 'Running tests'
                sh '''#!/usr/bin/env bash
                source setup-environment.sh
                python test-lib.py
                '''
            }
        }
        stage('Linters') { 
            steps {
                echo 'Running linter'
                sh '''#!/usr/bin/env bash
                source setup-environment.sh
                python test-lint.py
                '''
            }
        }
    }
    post {
        always {
            echo 'Build completed'
        }
        success {
            echo 'Build was successful'
            cleanWs()
        }
        failure {
            echo 'Build failed'
        }
        unstable {
            echo 'Build unstable'
        }
        changed {
            echo 'Build status changed'
        }
    }
}