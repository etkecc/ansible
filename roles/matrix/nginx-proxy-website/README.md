# matrix/nginx-proxy-website

That role deploys your website to your matrix's base domain.

## Requirements

1. Put following in your matrix host's vars.yml file:

```yml
matrix_nginx_proxy_base_domain_homepage_enabled: false
matrix_nginx_proxy_website_enabled: true
```

it will disable `Hello from DOMAIN!` index.html file automatically generated by matrix-nginx-proxy role
and allow you to put any content you want to website folder

2. You should have git (and website builder, if you use it) installed control/host machine where you run that role

## Configuration

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options

### matrix_nginx_proxy_website_repo

Your website git url, eg: `https://gitlab.com/rakshazi/rakshazi.me.git`

### matrix_nginx_proxy_website_command

The command to build website, default value (usable only for hugo sites): `hugo --i18n-warnings --ignoreCache --path-warnings --minify`

NOTE: you can set empty `""` command if you don't need to run anything

### matrix_nginx_proxy_website_dist

Website build's artifact folder (dist path), default value: `public`

NOTE: that should be folder name, without slashes or absolute path,
but **if** you want just copy content of your website's git repo, put an empty value `""` to that var.