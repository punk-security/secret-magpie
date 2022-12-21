[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/punk-security/secret-magpie-cli/graphs/commit-activity)
[![Maintaner](https://img.shields.io/badge/maintainer-PunkSecurity-blue)](https://www.punksecurity.co.uk)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=punk-security_secret-magpie-cli&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=punk-security_secret-magpie-cli)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=punk-security_secret-magpie-cli&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=punk-security_secret-magpie-cli)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=punk-security_secret-magpie-cli&metric=bugs)](https://sonarcloud.io/summary/new_code?id=punk-security_secret-magpie-cli)

```
          ____              __   _____                      _ __       
         / __ \__  ______  / /__/ ___/___  _______  _______(_) /___  __
        / /_/ / / / / __ \/ //_/\__ \/ _ \/ ___/ / / / ___/ / __/ / / /
       / ____/ /_/ / / / / ,<  ___/ /  __/ /__/ /_/ / /  / / /_/ /_/ / 
      /_/    \__,_/_/ /_/_/|_|/____/\___/\___/\__,_/_/  /_/\__/\__, /  
                                             PRESENTS         /____/  
                              Secret-Magpie ✨

      Scan all your github/bitbucket repos from one tool, with multiple tools!
```                                                       
    
# SecretMagpie 

## Intro

SecretMagpie is a secret detection tool that hunts out all the secrets hiding in your GitHub repositories. It uses multiple tools in one convenient package to scan every branch of every repository in an organisation. It then smooshes all those results together into a lovely json output and reports some big ticket stats right to the screen. 

By making use of the opensource tools [Trufflehog](https://github.com/trufflesecurity/trufflehog) 🐷 and [Gitleaks](https://github.com/zricethezav/gitleaks), SecretMagpie can highlight a variety of different secrets and ensure that nothing is missed!

## Docker

We've kept things nice and simple and bundled everything into a Docker container to enable you to start finding secrets as soon as possible. SecretMagpie has two mandatory parameters, a GitHub organisation name and a GitHub personal access token.

Simply run one of the following commands to get started:
```shell
docker run punksecurity/secret-magpie github --org 'github organisation name' --pat 'personal access token'
```
or
```shell
docker run punksecurity/secret-magpie bitbucket --workspace 'workspace name to scan' --username 'your username' --password 'your application password'
```
or
```shell

docker run -v /local/path/to/repos/:/repos punksecurity/secret-magpie filesystem --path /repos
```
## Get your results
Copy from the container

```
docker cp 'container':/app/results/results.[csv/json] /host/path/target
```
OR Mount the volume

```
docker -v /localpath:/app/results
```
## Installation

If you prefer not to use Docker then you will need to manually install the following:

* Python 3.10
* Git
* [Trufflehog 3.20.0](https://github.com/trufflesecurity/trufflehog/releases/tag/v3.20.0) installed and on PATH
* [Gitleaks v8.15.2](https://github.com/zricethezav/gitleaks/releases/tag/v8.15.2) installed and on PATH

You will also need to install the dependencies in requirements.txt by running the following command:

```
pip install -r requirements.txt
```


## Full Usage

```
usage:
 .\main.py {bitbucket/github/filesystem} [options]

positional arguments:
  {github,bitbucket,filesystem}

options:
  -h, --help            show this help message and exit
  --out OUT             Output file (default: results)
  --no-cleanup          Don't remove checked-out repositories upon completion
  --out-format {csv,json}
  --parallel-repos PARALLEL_REPOS
                        Number of repos to process in parallel - more than 3 not advised (default: 5)
  --disable-trufflehog  Scan without trufflehog
  --disable-gitleaks    Scan without gitleaks
  --single-branch       Scan only the default branch
  --dont-store-secret   Do not store the plaintext secret in the results
  --no-stats            Do not output stats summary

github:
  --org ORG             Github organisation name to target
  --pat PAT             Github Personal Access Token for API access and cloning

bitbucket:
  --workspace WORKSPACE
  --username USERNAME
  --password PASSWORD

filesystem:
  --path PATH           The root directory that contains all of the repositories to scan. Each repository should be a subdirectory under this path.
```

![CMD](Docs/secret-magpie.gif)
