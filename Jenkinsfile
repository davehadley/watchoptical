ipeline {
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
                ./build.sh
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
        stage('watchoptical') { 
            stages {
                stage('Build ROOT Extensions') {
                    steps {
                        echo 'Install watchoptical'
                        sh '''#!/usr/bin/env bash
                        source setup-environment.sh
                        pip install -e ./watchoptical
                        '''
                    }
                }
                stage('Build NCFGD') {
                    steps {
                        echo 'Build NCFGD'
                        sh '''#!/usr/bin/env bash
                        source setup-environment.sh
                        pip install ./ncfgd
                        '''
                    }
                }
                stage('Build NCFGD Runner') {
                    steps {
                        echo 'Build NCFGD Runner'
                        sh '''#!/usr/bin/env bash
                        source setup-environment.sh
                        pip install ./ncfgdrunner
                        '''
                    }
                }
                stage('Test ROOT Extensions') {
                    stages {
                        stage('Pytest') {
                            steps {
                                echo 'Testing ROOT Extensions'
                                sh '''#!/usr/bin/env bash
                                source setup-environment.sh
                                pytest ncfgdrootext/tests
                                '''
                            }
                        }
                        stage('Lint') {
                            stages {
                                stage('Black') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        black --check ncfgdrootext/src/ ncfgdrootext/tests
                                        '''
                                    }
                                }
                                stage('MyPy') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        mypy --no-strict-optional --ignore-missing-imports ncfgdrootext/src/ ncfgdrootext/tests
                                        '''
                                    }
                                }
                                stage('Flake8') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        flake8 ncfgdrootext/src/ ncfgdrootext/tests
                                        '''
                                    }
                                }
                            }
                        }
                    }
                }
                stage('Test NCFGD') {
                    stages {
                        stage('Pytest') {
                            steps {
                                echo 'Testing NCFGD'
                                sh '''#!/usr/bin/env bash
                                source setup-environment.sh
                                pytest ncfgd/tests
                                '''
                            }
                        }
                        stage('Lint') {
                            stages {
                                stage('Black') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        black --check ncfgd/src/ncfgd ncfgd/tests
                                        '''
                                    }
                                }
                                stage('MyPy') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        mypy --no-strict-optional --ignore-missing-imports ncfgd/src/ncfgd ncfgd/tests
                                        '''
                                    }
                                }
                                stage('Flake8') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        flake8 ncfgd/src/ncfgd ncfgd/tests
                                        '''
                                    }
                                }
                            }
                        }
                    }
                }
                stage('Test NCFGD Runner') {
                    stages {
                        stage('Pytest') {
                            steps {
                                echo 'Testing NCFGD Runer'
                                sh '''#!/usr/bin/env bash
                                source setup-environment.sh
                                pytest ncfgdrunner/tests
                                '''
                            }
                        }
                        stage('Lint') {
                            stages {
                                stage('Black') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        black --check ncfgdrunner/src ncfgd/tests
                                        '''
                                    }
                                }
                                stage('MyPy') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        mypy --no-strict-optional --ignore-missing-imports ncfgdrunner/src ncfgdrunner/tests
                                        '''
                                    }
                                }
                                stage('Flake8') {
                                    steps {
                                        sh '''#!/usr/bin/env bash
                                        source setup-environment.sh
                                        flake8 ncfgdrunner/src ncfgdrunner/tests
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