#! /bin/bash

echo "== mock git server"
echo ""
echo "Start by verifying you can ssh to the svn container:"
echo " \$ ssh -i ~/.ssh/id-blank svnuser@svnserver"
echo " \$ ssh -i ~/.ssh/id-keyed svnuser@svnserver   (keyphrase is 'keyed')"
echo ""
echo "Then run:"
echo " \$ subgit configure svn+ssh://svnserver/svn/Project1 Project1.git"
echo ""

TEST_CONFIG="subgit-test-config"
if [ ! -f "${TEST_CONFIG}" ]; then
	cp /ssh-keys/${TEST_CONFIG} ~/"${TEST_CONFIG}"
fi
echo "See $(pwd)/${TEST_CONFIG} for an example config to use after configure"

