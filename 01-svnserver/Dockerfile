# Originally written by Oliver "kfsone" Smith <oliver@kfs.org>
#
# Dockerfile that creates a trivial svn server instance with a populated repos, and
# generates ssh keys to be used by the second server for accessing this one.
#
#  - repository is /svn
#  - group is svn
#  - adds a user called svnuser
#  - top-level paths '^/Project1' and '^/Project2' with Trunk/ and Branches/ structure
#  - ssh-keys are generated in /tmp/ssh-keys
#  - when the entrypoint is invoked, the ssh-keys are copied to the /ssh-keys volume.
#
# There are two keys:
#  - id-blank   -   ecdsa with no passphrase
#  - id-keyed   -   ecdsa with 'keyed' as the passphrase
#

# -----------------------------------------------------------------------------
# First layer: packages and users.
FROM ubuntu:20.04 AS base

# Ready APT packages
RUN apt update && \
	apt install -qy openssh-server subversion nano vim && \
	apt clean

# Create an 'svn' group
RUN groupadd svn

# Create a top-level /svn folder, owned by the svn group
RUN mkdir --mode 0776 /svn && chgrp svn /svn

# Create an svn user account, 'svnuser'
RUN	useradd -ms /bin/bash -G svn svnuser


# -----------------------------------------------------------------------------
# Second layer: populate the SVN image.
FROM base as population

USER svnuser

# Create the /svn repository, empty
WORKDIR /home/svnuser
RUN svnadmin create /svn

# Create a working directory to create commits in
WORKDIR /home/svnuser
RUN svn checkout file:///svn /home/svnuser/svn.checkout


# Create first commit with project-based structure, and with
# Trunk as the master branch and Branches the container for branches.
WORKDIR /home/svnuser/svn.checkout
RUN mkdir Project1										&& \
	svn add Project1									&& \
	mkdir Project1/Trunk Project1/Branches				&& \
	svn add Project1/Trunk Project1/Branches			&& \
	echo "# Welcome to Project1"						   \
		 >Project1/Trunk/README.md 						&& \
	svn add Project1/Trunk/README.md					&& \
	svn commit -m "Initial commit" .					&& \
	svn update .

# Create a branch
RUN svn copy -m "Dev Branch" file:///svn/Project1/Trunk file:///svn/Project1/Branches/DevBranch && \
	svn update .

# Create a fork
RUN svn copy -m "Project2 fork" file:///svn/Project1 file:///svn/Project2 && \
	svn update .

# Make changes to the fork.
RUN	echo "# Welcome to Project2, at last"				   \
		 >Project2/Trunk/README.md						&& \
	svn commit -m "Fork: Project2" Project2				&& \
	svn update .


# -----------------------------------------------------------------------------
# Third layer: enable ssh (from other containers)
FROM population as ssh-setup

ENV SSH_KEY_TYPE rsa

# System SSH key
USER root
RUN	 ssh-keygen -A && mkdir /run/sshd

# Create ssh keys locally, so that the run script can expose them to other containers.
RUN	 mkdir /tmp/ssh-keys

# Create pairs of keys: one with the passphrase "keyed" and the other with a blank passphrase
# NOTE: use pem format, because subgit requires it.
RUN	 ssh-keygen -m pem -t ${SSH_KEY_TYPE} -f /tmp/ssh-keys/id-keyed -N "keyed" && \
	 ssh-keygen -m pem -t ${SSH_KEY_TYPE} -f /tmp/ssh-keys/id-blank -N ""      && \
	 echo "${SSH_KEY_TYPE}" >/tmp/ssh-keys/key-type

# Populate svnuser's .ssh folder, authorize both keys, fix permissions
RUN  mkdir --mode 0760 ~svnuser/.ssh && \
	 cat /tmp/ssh-keys/*.pub >~svnuser/.ssh/authorized_keys && \
	 cp /tmp/ssh-keys/* ~svnuser/.ssh/ && \
	 chown -R svnuser.svnuser ~svnuser/.ssh && \
	 chmod 0600 ~svnuser/.ssh/authorized_keys && \
	 cat ~svnuser/.ssh/authorized_keys


# -----------------------------------------------------------------------------
# Final layer:
#
# Copy the runtime script and make it the entry point.
FROM ssh-setup
COPY ./entrypoint.sh /entrypoint.sh
VOLUME /ssh-keys
ENTRYPOINT ["/bin/bash", "-c", "/entrypoint.sh"]

