# matrix/backup-borg

Role to install borg backup and borgmatic on your matrix server.

## Requirements & install

1. Create ssh key:

```bash
ssh-keygen -t ed25519 -N '' -C matrix
```

2. Add public part of that ssh key to your borg provider / server:

```bash
# example to append the new PUBKEY contents, where:
# PUBKEY is path to the public key,
# USER is a ssh user on a provider / server
# HOST is a ssh host of a provider / server
cat PUBKEY | ssh USER@HOST 'dd of=.ssh/authorized_keys oflag=append conv=notrunc'
```

3. Put following in your matrix host's vars.yml file:

```yml
matrix_backup_borg_enabled: true
matrix_backup_borg_repository: "USER@HOST:REPO"
matrix_backup_borg_passphrase: "PASSPHRASE"
matrix_backup_borg_ssh_key: |
	PRIVATE KEY
```

where:

* USER - ssh user of a provider / server
* HOST - ssh host of a provider / server
* REPO - borg repository name, it will be initialized on backup start, eg: `matrix`
* PASSPHRASE - super-secret borg passphrase, you may generate it with `pwgen -s 64 1` or use any password manager
* PRIVATE KEY - the content of the public part of the ssh key you created before
