#! /bin/bash

function die() {
	echo -e "\e[31;1mERROR: $*\e[0m"
	exit 22
}

rm -rf /tmp/new-ssh-keys
mkdir /tmp/new-ssh-keys
for key_type in rsa dsa ecdsa ed25519; do
  for mode in openssh pem; do
    mode_arg=$([ "$mode" == "pem" ] && echo "-m $mode" || echo "")
    for key in blank keyed; do
      key_arg=$([ "$key" == "blank" ] && echo "" || echo "$key")
      ssh-keygen -f "/tmp/new-ssh-keys/id-${key_type}-${mode}-${key}" -t $key_type $mode_arg -N "$key_arg" || \
		  die "failed generating $key_type $mode $key key."
    done
  done
done
