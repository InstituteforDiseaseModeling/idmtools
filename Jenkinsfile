def repo_ssh_url
def default_branch ='main'

pipeline {
    environment {
        user = credentials('Comps_emodpy_user')
        COMPS_PASS = credentials('Comps_emodpy_password')
        PYPI_STAGING_USERNAME =  credentials('idm_bamboo_user')
        PYPI_STAGING_PASSWORD = credentials('idm_bamboo_user_password')
    }
    agent {
        node {
            label "idmtools_slurm"
        }
    }
    stages {
        stage("Clean previous dir and virtual environment") {
            steps {
                dir("${WORKSPACE}") {
                    deleteDir()
                }
                sh 'ls -lart'
                echo 'Remove disk_cache to avoid pickle issue'
                sh 'rm -fr ~/.idmtools/cache/disk_cache/platforms/'
            }
        }
        stage("Build URL and path") {
            steps {
                script {
                    repo_ssh_url = "git@github.com:InstituteforDiseaseModeling/idmtools.git"
                    default_branch = "main"
                    echo "workspace is ${WORKSPACE}"
                }
            }
        }
		stage('Code Checkout') {
			steps {
				script {
					if (env.CHANGE_ID) {
						echo "I execute on the pull request ${env.CHANGE_ID}"
						checkout([$class: 'GitSCM',
						branches: [[name: "pr/${env.CHANGE_ID}/head"]],
						doGenerateSubmoduleConfigurations: false,
						extensions: [],
						gitTool: 'Default',
						submoduleCfg: [],
						userRemoteConfigs: [[refspec: '+refs/pull/*:refs/remotes/origin/pr/*', credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2', url: repo_ssh_url]]])
					} else {
						echo "I execute on the ${env.BRANCH_NAME} branch"
						git branch: "${env.BRANCH_NAME}",
						credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2',
						url: repo_ssh_url
					}
					sh 'ls -lart'
				}
			}
		}

        stage('Create virtual environment'){
            steps {
                script {
                    withPythonEnv("/usr/bin/python3.10") {
                        sh 'pip list'
                    }
                }
            }
        }
        stage("Prepare") {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh 'pip install idm-buildtools flake8 wheel pygit2 matplotlib sqlalchemy natsort pytest --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple'
                            sh 'make setup-dev-no-docker'
                            sh 'pip list'
                            sh 'python dev_scripts/create_auth_token_args.py --comps_url https://comps2.idmod.org --username idmtools_bamboo'
                        }
                    }
                }
            }
        }
        stage('Run idmtools slurm example') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh 'python examples/native_slurm/python_sims.py'
                            sh 'ls -lart ~/example/'
                        }
					}
                }
            }
        }
        stage('run cli tests') {
            //success = false
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh '''#!/bin/bash
                            cd idmtools_cli
                            PARALLEL_TEST_COUNT=2 make test-all
                            '''
                        }
					}
                }
            }
        }
        stage('run core tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh '''#!/bin/bash
                            cd idmtools_core
                            PARALLEL_TEST_COUNT=2 make test-all
                            '''
                        }
					}
                }
            }
        }
        stage('run platform_slurm tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh '''#!/bin/bash
                            cd idmtools_platform_slurm
                            make test-all
                            '''
                        }
                    }
                }
            }
        }
        stage('run models tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh '''#!/bin/bash
                            cd idmtools_models
                            PARALLEL_TEST_COUNT=2 make test-all
                            '''
                        }
					}
                }
            }
        }
        stage('run slurm utils tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh '''#!/bin/bash
                            cd idmtools_slurm_utils
                            make test-all
                            '''
                        }
                    }
                }
            }
        }
        stage('run platform_general tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh '''#!/bin/bash
                            cd idmtools_platform_general
                            make test-all
                            '''
                        }
					}
                }
            }
        }
        stage('Run idmtools platform comps tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                script {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh '''#!/bin/bash
                            cd idmtools_platform_comps
                            PARALLEL_TEST_COUNT=2  make test-all
                            '''
                        }
					}
                }
            }
        }
    }
    post {
        // Clean after build
        always {
            junit(
                allowEmptyResults: true,
                testResults: '**/*test_results.xml',
                skipPublishingChecks: true
            )
            cleanWs()
            dir("/home/jenkins/example") {
                deleteDir()  //this is slurm example result
            }
        }
    }
}
