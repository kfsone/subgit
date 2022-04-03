#! /usr/bin/env python3 -B

from collections import defaultdict
from pathlib import Path
import logging
import shutil
import subprocess
import sys


# DSA known not to work
ALLOWED_KEY_TYPES = ("rsa", "ecdsa", "ed25519")  # , "dsa")
ALLOWED_FORMATS   = ("openssh", "pem")
KEYING_PHRASES    = {"blank": "", "keyed": "keyed"}

SVN_USER          = "svnuser"
SVN_SERVER        = "svnserver"
SVN_PROTOCOL      = "svn+ssh"
SVN_REPOS         = "svn"
SVN_PROJECT       = "Project1"

SVN_URL           = f"{SVN_PROTOCOL}://{SVN_SERVER}/{SVN_REPOS}/{SVN_PROJECT}"


CONFIGS_DIR       = Path("/configs")
SSH_DIR           = Path("~/.ssh").expanduser().resolve()

TEMPLATE          = CONFIGS_DIR / "config.template"

PROJECT_DIR       = Path("~", SVN_PROJECT + ".git").expanduser().resolve()

RECORD_PREFIX     = "tryconfigs.attempt"

FAILURES          = defaultdict(list)


logger = logging.getLogger("tryconfigs")

def execute(cmd: str):
    logger.debug("execute: %s", cmd)
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class Tester:
    def __init__(self, config_dir: Path, ssh_dir: Path, template_file: Path) -> None:
        assert config_dir.exists()
        self.config_dir = config_dir

        assert ssh_dir.exists()
        self.ssh_dir = ssh_dir

        assert template_file.exists()
        self.template = template_file.read_text()

        self.keys = sorted(f for f in self.ssh_dir.glob(f"id-*-*-*.pub"))

        print(
                f"-- config_dir: {config_dir}\n"
                f"-- ssh_dir   : {ssh_dir}\n"
                f"-- template  : {template_file}\n"
                f"-- ssh keys  : {len(self.keys)}\n"
        )

        self.test_no = 0

    def test(self, key_type, key_format, key_phrase, with_user, with_name, with_phrase) -> None:
        if not (with_user or with_name):
            # produces an invalid config that says "username must be supplied"
            return

        self.test_no += 1
        config_file = Path(PROJECT_DIR, "subgit", "config")
        keyfile     = Path(self.ssh_dir, f"id-{key_type}-{key_format}-{key_phrase}")

        print(
            f"#{self.test_no:3}: "
            f"key:{key_type:8}, "
            f"format:{key_format:8}, "
            f"phrase:\"{key_phrase:8}\", "
            f"w/user:{with_user:5}, "
            f"w/name:{with_name:5}, "
            f"w/phrase:{with_phrase} -> {config_file}:"
        )

        if PROJECT_DIR.exists():
            logger.debug("Removing %s", PROJECT_DIR)
            shutil.rmtree(PROJECT_DIR)

        result = execute(f"subgit configure {SVN_URL} {PROJECT_DIR}")
        if result.returncode != 0:
            raise RuntimeError("subgit configure failed: " + result.stderr)

        logger.debug("Writing %s", config_file)
        config_file.write_text(self.template.format(
            params     = f"key type: {key_type}, key file format: {key_format}, key passphrase: '{key_phrase}'",
            with_user  = f"{SVN_USER}@" if with_user else "",
            with_name  = f"userName = {SVN_USER}" if with_name else "",
            passphrase = f"sshKeyFilePassphrase = {KEYING_PHRASES.get(key_phrase, key_phrase)}" if with_phrase else "",
            keyfile    = keyfile,
        ))
        
        result = execute(f"subgit install {PROJECT_DIR}")
        if result.returncode == 0:
            print("SUCCESS!")
            sys.exit(0)

        log_file = Path(f"/tmp/{RECORD_PREFIX}.{key_type}.{key_format}.{key_phrase}.{with_user}.{with_name}.{with_phrase}.log")
        stdout, stderr = result.stderr.decode(), result.stdout.decode()
        log_file.write_text(f"--- stdout ---\n{stdout}\n\n --- stderr ---\n{stderr}\n")

        print("| -- Installation failed" if "INSTALLATION FAILED" in stderr else "| -- Failed?")
        if "error:" in stdout:
            errors = [line[7:].strip() for line in stdout.split('\n') if "error:" in line]
            error = errors[0]
            print("| --> " + error)

        else:
            error = "unknown"

        logger.debug("See: %s", log_file)
        print()

        execute(f"subgit uninstall {PROJECT_DIR}")
        
        FAILURES[error].append((key_type, key_format, key_phrase, with_user, with_name, with_phrase, log_file))


    def run(self) -> None:
        # Remove all the config-*.ini and result files from previous runs
        for ini in Path("/tmp").glob(RECORD_PREFIX + "*"):
            ini.unlink()

        # Iterate over the list of public key files and filter down to those
        # that look like generated ones.
        for key in self.keys:
            # all the keys are named, e.g. id-dsa-openssh-keyed.pub
            _, key_type, key_format, key_phrase = key.stem.split('-')

            if key_type not in ALLOWED_KEY_TYPES or key_format not in ALLOWED_FORMATS or key_phrase not in KEYING_PHRASES:
                continue

            for with_user in True, False:
                for with_name in True, False:
                    # Phrase is obligatory if the key has a passphrase
                    self.test(key_type, key_format, key_phrase, with_user, with_name, True)
                    if KEYING_PHRASES[key_phrase] == "":
                        self.test(key_type, key_format, key_phrase, with_user, with_name, False)


def main():
    result = execute(f"ssh {SVN_USER}@{SVN_SERVER} -i ~/.ssh/id-ecdsa-openssh-blank echo ok")
    if result.returncode != 0:
        raise RuntimeError("Unable to confirm ssh connectivity. Make sure you have ssh'd at least once to populate known_hosts: " + result.stderr.decode())

    tester = Tester(CONFIGS_DIR, SSH_DIR, TEMPLATE)
    tester.run()

    print("Error Summary:")
    for error, items in FAILURES.items():
        print(f"{len(items)}x\"{error}\"\n")


if __name__ == "__main__":
    log_at = logging.DEBUG if len(sys.argv) == 2 and sys.argv[1] == "--debug" else logging.INFO
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(log_at)

    main()
