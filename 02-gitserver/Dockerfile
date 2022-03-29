# Originally written by Oliver "kfsone" Smith <oliver@kfs.org>
#
# Dockerfile that creates a basic setup for reproducing issues with subgit configure/install.
#
#  - installs various packages,
#  - adds a distinct user (so username must be specified),
#  - imports the ssh keys from the ssh keys volume
#  - group is svn
#  - adds a user called gituser
#  - top-level paths '^/Project1' and '^/Project2' with Trunk/ and Branches/ structure
#  - ssh-keys are generated in /tmp/ssh-keys
#  - when the entrypoint is invoked, the ssh-keys are copied to the /ssh-keys volume.
#
# There are two keys:
#  - id-blank   -   ecdsa with no passphrase
#  - id-keyed   -   ecdsa with 'keyed' as the passphrase
#


# ------------------------------------------------------------------------------
# First Layer: packages
#
FROM ubuntu:20.04 AS base

RUN	echo 'Acquire::Http::Proxy "http://wafer.lan:3142/";' >/etc/apt/apt.conf.d/02proxy

RUN apt update && \
	apt install -qy openssh-client subversion wget openjdk-17-jre-headless vim nano

# Fetch the subgit package and install it
RUN wget -O subgit.deb https://subgit.com/files/subgit_3.3.13_all.deb
RUN dpkg -i subgit.deb && rm subgit.deb

# Fix apt packages
RUN	apt install -f

# Cleanup
RUN	apt clean


# ------------------------------------------------------------------------------
# Second Layer: configure gituser account
#
FROM base as with-user

RUN	useradd -ms /bin/bash gituser
RUN mkdir --mode 0760 ~gituser/.ssh && chown gituser.gituser ~gituser/.ssh

COPY ./bashrc /tmp/bashrc
COPY ./bash_history /home/gituser/.bash_history
RUN cat /tmp/bashrc >>~/.bashrc && rm /tmp/bashrc && chown gituser.gituser ~gituser/.bash*


# ------------------------------------------------------------------------------
# Third Layer: configure gituser account
#
FROM with-user

USER root
COPY ./entrypoint.sh /entrypoint.sh

VOLUME /ssh-keys

WORKDIR /home/gituser
ENTRYPOINT ["/bin/bash", "-c", "/entrypoint.sh"]
