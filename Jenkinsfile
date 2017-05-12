#!/usr/bin/env groovy

node('!master') {
  stage('Deploy') {
    step([$class: 'WsCleanup'])

    checkout scm
    
    if (env.BRANCH_NAME == 'master'){
      lock(resource: 'infrastructure-deployment', inversePrecedence: true) {
        stage('Deploy') {
          sh "ssh deployer deploy deployer prod"
        }
      }
      milestone()
    }
  }
}