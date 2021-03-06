#! /bin/bash
#
# Entrypoint for the gitserver container:
#
#  - imports the ssh keys generated by the svnserver container,
#  - runs sleep to keep the container alive.

# Install the shared ssh keys
cp /ssh-keys/id* /home/gituser/.ssh/
cp /ssh-keys/*config* /home/gituser/
chown -R gituser.gituser /home/gituser/
chmod 0600 /home/gituser/.ssh/*

echo -n "use 'docker exec -it 02-subgit /bin/bash' to enter the container environment."
sleep 999999
