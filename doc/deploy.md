# Deploying the gitlab runner

<!--toc:start-->
- [Deploying the gitlab runner](#deploying-the-gitlab-runner)
  - [Introduction](#introduction)
  - [Deployment](#deployment)
    - [Host Setup](#host-setup)
    - [Registering GitLab Runner](#registering-gitlab-runner)
  - [Configuration](#configuration)
<!--toc:end-->

## Introduction
To test nitrokey firmware directly through GitLab CI, a GitLab Runner has to be registered. The runner will execute inside of a podman container.
An automated setup for the host machine is provided for fedora machines as follows.

## Deployment
The Runner is set up to run in a rootless podman container so make sure podman is installed. In the following steps the active user is expected to have sudo privileges.

### Host Setup
The calling below should do cockpit installation and other user setup for the GitLab runner automatically:

```commandline
make setup-fedora-host
```

This realizes the following:

1. Install udev rules (a local variation of libnitrokey's rules - see /bin/41-nitrokey-test.rules; this includes YKush support)
2. Install cockpit package and activate it
3. Add user for the Gitlab Runner service, and set "linger" attribute on it
4. Setup autostart service
5. Build Podman image for the Gitlab Runner (in future this will download a prebuilt one, instead of building it locally)

Once the image is built, the runner needs to be registered.

### Registering GitLab Runner
1. Go to "new runner" page (change example repo to your repo):
    - https://git.mydomain.com/myuser/myrepo/-/runners/new
2. Set platform "Linux"
3. Set `nk3-hw` tag
4. Add details describing the added machine
5. Check [x] `Lock to current projects`
6. Set timeout 3600
7. Press "create runner"
8. You'll get multiple steps guide with instructions similar to:
   ```commandline
    gitlab-runner register --url https://git.mydomain.com
       --token glrt-ABCABCABCABCABCABCAB
    ```
   (note that the token you will get should be different, and the one here is not valid)
10. Open a shell in the container
    ```commandline
      make gl-runner-enter
    ```
11. Enter the commands listed on the page in the container's shell (similar to the one in step 8)
12. Follow the TUI wizard for registration:
    - instance: `git.mydomain.com` (default)
    - name of the container: make descriptive id — this will be shown on the runner's status page
    - executor: `shell`
13. Close `podman exec` terminal to the container.
    - `exit`
14. The configuration should be reloaded now, and the runner should
    register itself within the Gitlab instance automatically
15. Confirm that the new runner is visible at:
    - https://git.mydomain.com/myuser/myrepo/-/settings/ci_cd#js-runners-settings
16. Configuration will be stored inside the mounted volume: `gitlab-runner-config`.
    It can be edited by:
    - inspecting the path of the volume and opening directly from the host machine (needs to be executed as user `nk3tests`):
        - `podman volume inspect gitlab-runner-config`
    - opening it inside the running container via `make gl-runner-enter` (can be executed as any user with sudo privileges):
        - `vi /etc/gitlab-runner/config.toml`

    Configuration file should be similar to this:
    ```toml
    concurrent = 1
    check_interval = 0
    shutdown_timeout = 0
    
    [session_server]
      session_timeout = 1800
    
    [[runners]]
      name = "office-pc"
      url = "https://git.mydomain.com"
      id = 33
      token = "glrt-ABCABCABCABCABCABCAB"
      token_obtained_at = 2023-09-19T16:39:27Z
      token_expires_at = 0001-01-01T00:00:00Z
      executor = "shell"
      [runners.cache]
        MaxUploadedArchiveSize = 0
    ```
17. Make sure the `concurrent` field is set to `1` in the configuration mentioned in the previous step


## Configuration
The container is started using podman quadlets, configuration is documented here: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html

### Configuring the podman quadlet
- Before changing anything stop the running container: `make gl-runner-stop`
- Configuration files are stored in the home directory of the nk3tests user. For convenience you can log into that user: `sudo -i -u nk3tests`
- Change what you need in `.config/containers/systemd/nk3-tests.container`
- When ready you can start the container again (user with sudo): `make gl-runner-start`
- To check on the container: `make gl-runner-status`

### Configuring gl-runner image
1. Stop running container 
  - `make gl-runner-stop`
2. To change the image log in as nk3tests
  - `sudo -i -u nk3tests`
3. Change what you need in `docker/Dockerfile-runner` and / or `docker/runner-entrypoint`
4. Build image (you can replace tag `testing` with what you want other than latest)
  - `podman build docker/ -t glab-runner-fedora:testing -f docker/Dockerfile-runner`
5. [Configure the quadlet to use the image tag you set](#configuring-the-podman-quadlet)
6. Start the container again
7. To get back to the normal state configure the quadlet to use tag `latest` again
