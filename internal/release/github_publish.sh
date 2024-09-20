#!/usr/bin/env bash

set -eu

GITHUB_REMOTE=git@github.com:fnproject/fdk-python.git
BITBUCKET_REMOTE=ssh://git@bitbucket.oci.oraclecorp.com:7999/faas/fdk-python.git
PUBLISH_BRANCH=github
TARGET_BRANCH=master
GIT_USER_EMAIL=ci@fnproject.com
GIT_USER_NAME=CI
SSH_KEY_SECRET=ocid1.vaultsecret.oc1.phx.amaaaaaaepf6idia24xnntsofwsbezkna5zzgdv3twbuv2eav5gxn7g6ezrq

TEMPDIR=$(mktemp -d)
cd ${TEMPDIR}
function cleanup {
    rm -rf ${TEMPDIR}
}
trap cleanup EXIT

KEY=$(oci secrets secret-bundle get --auth security_token --region us-phoenix-1 --secret-id ${SSH_KEY_SECRET} --raw-output --query 'data."secret-bundle-content".content' | base64 -D)
echo "$KEY" >key
chmod 600 key

export GIT_SSH_COMMAND="ssh -i ${TEMPDIR}/key"
git clone ${GITHUB_REMOTE} github
git clone ${BITBUCKET_REMOTE} bitbucket

pushd bitbucket
git fetch
git checkout ${PUBLISH_BRANCH}
git reset --hard origin/${PUBLISH_BRANCH}
popd

pushd github
git fetch
git checkout ${TARGET_BRANCH}
git reset --hard origin/${TARGET_BRANCH}
git remote add bitbucket ../bitbucket
git fetch bitbucket
git config user.email ${GIT_USER_EMAIL}
git config user.name ${GIT_USER_NAME}
git merge --ff bitbucket/${PUBLISH_BRANCH}
git push