# integration/git2bunny

That role uploads files from git repo to BunnyCDN storage

## Requirements

1. Put following in your matrix host's vars.yml file:

```yml
integration_git2bunny_enabled: true
integration_git2bunny_repo: "https://git.repo/url.git"
integration_git2bunny_zone: "storage-zone-name"
integration_git2bunny_accesskey: "storage-access-key"
```

2. You should have git installed control/host machine where you run that role

## Configuration

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options
