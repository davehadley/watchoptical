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
        stage('watchopticalmc') { 
            stages {
                stage('Test watchopticalmc') {
                    stages {
                        stage('pytest') {
                            steps {
                                echo 'Testing watchopticalmc'
                                sh '''#!/usr/bin/env bash
                                source setup-environment.sh
                                pytest lib/watchopticalmc/tests
                                '''
                            }
                        }
                        stage('Lint') {
                            stages {
                                stage('Black') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        black --check lib/watchopticalmc/watchoptical lib/watchopticalmc/tests
                                        '''
                                    }
                                }
                                stage('MyPy') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        mypy --no-strict-optional --ignore-missing-imports lib/watchopticalmc/watchoptical lib/watchopticalmc/tests
                                        '''
                                    }
                                }
                                stage('Flake8') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        flake8 lib/watchopticalmc/watchoptical lib/watchopticalmc/tests
                                        '''
                                    }
                                }
                            }
                        }
                    }
                }
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