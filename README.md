Docker experiment for SubGit svn+ssh configuration
==================================================

# Scenario

This docker config creates two containers:

1. "svnserver": a simple container with a small svn-repository configured
as /svn, a user called 'svnuser', some ssh keys, and an ssh daemon that can
be used to access the repository from another container.

2. "gitserver": an even simpler container with subgit, an ssh client, and
ssh keys needed to access the first container, but the user is called 'gituser'
to prevent coincidental matching of usernames.


# Purpose

Use this config to bootstrap an svn+ssh:// accessible repository from
a freshly purposed git server to debug issues using the 'svn+ssh' protocol
from subgit.


# Usage

```bash
# bring the service up
docker compose up
# or: docker compose up -d   # if you don't care to see output from the containers

# switch to another console and run:
docker compose exec -u gituser -it gitserver /bin/bash
```

## Expected output:

Expect to see something along the lines of:

```
$ docker compose up
[+] Running 3/3
 - Network subgit_default        Created
 - Container subgit-svnserver-1  Created
 - Container subgit-subgit-1     Created
   Attaching to subgit-subgit-1, subgit-svnserver-1
   subgit-svnserver-1  | -- Exporting ssh keys to ssh-keys volume.
   subgit-svnserver-1  | -- Starting container-only sshd in the background
   subgit-svnserver-1  | -- Tailing sshd log
   subgit-svnserver-1  | Server listening on 0.0.0.0 port 22.
   subgit-svnserver-1  | Server listening on :: port 22.
```

At this point, the experiment is live, and waiting for you to exec into it.

# Notes

Neither container exposes any ports outside the container network, so you need
to use 'docker exec' to get into the container.

Neither container runs any active proceses: the svnserver just runs an sshd and
then tails the ssh server's log to keep the container alive; the gitserver just
imports ssh keys from the first container and then sits in a sleep so you can
exec into it.


# Mass Tester

Python script `/configs/tryconfigs.py` can be used to bulk-test a whole slew
of configurations to test for a scenario that works.

It will attempt different config combos until it finds one that works and
then stop, or it will proceed until all combinations are exhausted and print
a summary report of the different errors that occured.

Run with `--debug` for verbose logging.

```
$ cd /configs
$ python3 tryconfigs.py [--debug]
...
```


