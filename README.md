# GitHub Actions ownCloud deployment experiment

An experiment to use GitHub Actions to deploy a Python script to an ownCloud instance via webDAV.

## Summary

This project is an experiment:
- to use GitHub Actions as a Continuous Deployment tool
- to deploy a Python script into an ownCloud instance shared folder 
- using its WebDAV API via a Python WebDAV client run from a (different) Python script

## Structure

- `/.github/workflows/cd.yml`: sample GitHub Actions workflow for continuous deployment
- `/gha-client/webdav-deploy.py`: deployment script (Python WebDAV client) ran by the GitHub Actions workflow
- `/python-client/`: Python development environment for the `webdav-deploy.py` script
- `/server/`: local ownCloud runtime files (created and populated automatically when starting server)
- `docker-compose.yml`: Docker Compose setup for running local ownCloud server
- `placeholder_script.py`: placeholder representing the real script to be deployed

## Applying

To use this experiment in a real project:
- copy the GitHub Actions workflow and `webdav-deploy.py` script (probably renamed)
- set secrets and variables in GitHub repo

## Usage

Start CloudFlare tunnel to allow GitHub Actions to access local ownCloud:

```
$ cloudflared tunnel --config ~/.cloudflared/ma-owncloud-exp run
```

Then make a repository change, commit and push to GitHub. 

On pushes to the `main` branch, the GitHub Actions workflow defined in `.github/workflows/cd.yml` will run. 

Verify the deployment is successful:
- the output of the workflow
- the `placeholder_script.py` is updated in ownCloud

## Developing

The deployment script is developed in `python-client/` as a Python Poetry project.

To setup:

```shell
# with Python and Poetry installed
$ cd python-client/
$ poetry install
```

A `.env` file is used for replicating the environment variables set by GitHub Actions.

Ideally code should be formatted with Black:

```
$ cd python-client/
$ poetry run black main.py
```

When updated:
- copy `main.py` to `../gha-client.py`
- remove the 'required for development' section (dotenv)

## Setup

This will:
- start an ownCloud server instance via Docker
- configure two users (a desktop user and an application user)
- configure a shared folder (CMF `exp-2023-01`)
- configure client syncing via ownCloud desktop client
- verify files can be created and synced via desktop client
- verify files can be created modified via a WebDAV client (HTTP)
- expose local ownCloud server through a CloudFlare tunnel (to allow remote access)
- create and configure a GitHub repo for deployments

### Requirements

- Docker Compose: `brew install --cask docker`
- ownCloud client: `brew install --cask owncloud`
- WebDAV client (e.g. Transmit), `brew install --cask transmit`
- Cloudflare zero-trust client (inc. a CF account and configured domain): `brew install cloudflared`
- GitHub account, with permissions to create repos, workflows and setting secrets

### Configure ownCloud server

Set the `OWNCLOUD_TRUSTED_DOMAINS` environment option to the domain configured in CloudFlare account.

```
$ docker compose up
```

Visit: http://localhost:8080

Login as:
- username: `admin`
- password: `password`

#### Create users

Visit: http://localhost:8080/settings/users

Create new user:
- username: `cwatson`
- email: `cwatson@mapaction.org`
- groups: `ma` (create as new group)

Once created, set password to `password` (make sure to hit enter after setting field, ignore email sending warning)

Create another new user:
- username: `jcinnamon`
- email: `jcinnamon@mapaction.org`
- groups: `ma`

Once created, set password to `password` (make sure to hit enter after setting field, ignore email sending warning)

In a private window, visit http://localhost:8080/settings/personal?sectionid=security and sign in as:
- username: `jcinnamon`
- password: `password`

Create a new app password:
- app name: `webdav`

Copy value somewhere persistent.

#### Create shared folder

From files section:
- create new folder: `exp-2023-01`
- open properties for new folder
- under *Sharing*, add `ma` group

### Configure ownCloud client

Run ownCloud client and add account:
- server address: `http://localhost:8080`
- username: `cwatson`
- password: `password`
- set sync options to sync the `exp-2023-01` directory only

### Verify ownCloud client

On local machine with ownCloud client running (as first user):

```
$ cd /path/to/exp-2023-01
$ touch foo.txt
```

Visit http://localhost:8080/apps/files/?dir=/exp-2023-01 and sign in as:
- username: `cwatson`
- password: `password`

Verify `foo.txt` file is present in file listing.

### Verify WebDAV client

On local machine with WebDAV client, create a new connection (as second user):
- server (HTTP): `localhost`
- port: `8080`
- username: `jcinnamon`
- password: *[app password set previously]*
- remote path: `/remote.php/dav/files/jcinnamon/`

Verify:
- `foo.txt` file is present in file listing
- `foo.txt` file can be edited

### Create CloudFlare tunnel

```shell
$ cloudflared tunnel login
$ cloudflared tunnel create ma-owncloud-exp

$ cat << EOF > ~/.cloudflared/ma-owncloud-exp
url: http://localhost:8080
tunnel: <Tunnel-UUID>
credentials-file: <Home-Dir>/.cloudflared/<Tunnel-UUID>.json
EOF

$ cloudflared tunnel route dns ma-owncloud-exp ma-owncloud-exp.<Configured-Domain>
```

Visit https://ma-owncloud-exp.<Configured-Domain> and login as:
- username: `admin`
- password: `password`

### Verify CloudFlare tunnel (via WebDAV client)

```
$ cloudflared tunnel --config ~/.cloudflared/ma-owncloud-exp run
```

On local machine with WebDAV client, create a new connection (as second user):
- server (HTTPS): `ma-owncloud-exp.<Configured-Domain>`
- port: `443`
- username: `jcinnamon`
- password: *[app password set previously]*
- remote path: `/remote.php/dav/files/jcinnamon/`

Verify:
- `foo.txt` file is present in file listing
- `foo.txt` file can be edited

### Create and configure GitHub repo

Visit https://github.com and create a new repo.

Go to *Settings* -> *Secrets* -> *Secrets and Variables* -> *Actions* -> *Secrets* and create items for:
- `OC_USERNAME`: `jcinnamon`
- `OC_PASSWORD`: `password`

Go to *Settings* -> *Secrets* -> *Secrets and Variables* -> *Actions* -> *Variables* and create items for:
- `OC_HOSTNAME`: `https://ma-owncloud-exp.<Configured-Domain>`

## License

Copyright (c) 2023 MapAction.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.