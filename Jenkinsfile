def repo_ssh_url
def default_branch
def repo_dir = 'idmtools-multipbranch-repo'

pipeline {
    parameters {
        choice(choices: ['python3.10', 'python3.7', 'python3.8', 'python3.9', 'python3.11'], name: 'PYTHON', description: 'python version')
    }
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
                dir(repo_dir) {
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
                    repo_ssh_url = "git@github.com:shchen-idmod/idmtools-1.git"
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
						extensions: [][$class: "RelativeTargetDirectory", relativeTargetDir: repo_dir]],
						gitTool: 'Default',
						submoduleCfg: [],
						userRemoteConfigs: [[refspec: '+refs/pull/*:refs/remotes/origin/pr/*', credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2', url: 'git@github.com:shchen-idmod/idmtools-1.git']]])
					} else {
						echo "I execute on the ${env.BRANCH_NAME} branch"
						git branch: "${env.BRANCH_NAME}",
						credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2',
						url: 'git@github.com:shchen-idmod/idmtools-1.git'
					}
				}
			}
		}

        stage('Create virtual environment'){
            steps {
                script {
                    dir(repo_dir) {
                        withPythonEnv("/usr/bin/python3.10") {
                            //sh 'pip install pytest'
                            sh 'pip list'
                        }
                    }
                }
            }
        }
        stage("Prepare") {
            steps {
                script {
                    dir(repo_dir) {
                        //withPythonEnv("/usr/bin/${params.PYTHON}") {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh 'pip install idm-buildtools flake8 wheel pygit2 matplotlib sqlalchemy natsort pytest --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple'
                            sh 'make setup-dev-no-docker'
                            sh 'python3 dev_scripts/create_auth_token_args.py --comps_url https://comps2.idmod.org --username idmtools_bamboo'
                            sh 'pip list'
                        }
                    }
                }
            }
        }
        stage('Run idmtools slurm example') {
            steps {
                script {
                    dir(repo_dir) {
                        withPythonEnv("/usr/bin/python3.10") {
                            sh 'python examples/native_slurm/python_sims.py'
                            sh 'ls -lart ~/example/'
                        }
                    }
                }
            }
        }
        stage('run cli tests') {
            steps {
                script {
                    withPythonEnv("/usr/bin/python3.10") {
                        //def cli_test_dir = repo_dir + '/idmtools_cli/'
                        dir(repo_dir + '/idmtools_cli/') {
                            sh '''#!/bin/bash
                            PARALLEL_TEST_COUNT=2 make test-all
                            '''
                        }
                    }
                }
            }
        }
        stage('run core tests') {
            steps {
                script {
                    withPythonEnv("/usr/bin/python3.10") {
                        dir(repo_dir + '/idmtools_core/') {
                            sh '''#!/bin/bash
                            PARALLEL_TEST_COUNT=2 make test-all
                            '''
                        }
                    }
                }
            }
        }
        stage('run platform_slurm tests') {
            steps {
                script {
                    withPythonEnv("/usr/bin/python3.10") {
                        dir(repo_dir + '/idmtools_platform_slurm/') {
                            sh '''#!/bin/bash
                            make test-all
                            '''
                        }
                    }
                }
            }
        }
        stage('run models tests') {
            steps {
                script {
                    withPythonEnv("/usr/bin/python3.10") {
                        dir(repo_dir + '/idmtools_models/') {
                            sh '''#!/bin/bash
                            PARALLEL_TEST_COUNT=2 make test-all
                            '''
                        }
                    }
                }
            }
        }
        stage('run slurm utils tests') {
            steps {
                script {
                    withPythonEnv("/usr/bin/python3.10") {
                        dir(repo_dir + '/idmtools_slurm_utils/') {
                            sh '''#!/bin/bash
                            make test-all
                            '''
                        }
                    }
                }
            }
        }
        stage('run platform_general tests') {
            steps {
                script {
                    withPythonEnv("/usr/bin/python3.10") {
                        dir(repo_dir + '/idmtools_platform_general/') {
                            sh '''#!/bin/bash
                            make test-all
                            '''
                        }
                    }
                }
            }
        }
        stage('Run idmtools platform comps tests') {
            steps {
                script {
                    withPythonEnv("/usr/bin/python3.10") {
                        dir(repo_dir + '/idmtools_platform_comps/') {
                            sh '''#!/bin/bash
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
