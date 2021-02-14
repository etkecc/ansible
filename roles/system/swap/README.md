# system/swap

That role creates swap file and configures system to mount it and use automatically

## Requirements

Put following in your matrix host's vars.yml file:

```yml
system_swap_enabled: true
```

## Configuration

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options

### system_swap_enabled

Enables the role, default: `true`

### system_swap_size

Total swap file size in megabytes, default: total ram * 2 (if total ram <= 2gb), else - 1gb

### system_swap_path

Path to the swap file, default: `/var/swap`

### system_swap_fallocate

Use fallocate to allocate space (otherwise dd will be used), default: `true`
