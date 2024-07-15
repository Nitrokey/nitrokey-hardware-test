PYTHON ?= 3.12

FILES=$(shell find -name "*.py" | grep -v tests/ | grep -v .venv/)

TESTS ?= pynitrokey

DOCKER ?= podman

.PHONY: init
init:
	uv venv --python "$(PYTHON)"
	uv pip install -r dev-requirements.txt

.PHONY: check ci glab-runner setup-fedora-host-user setup-fedora-host clean-setup-fedora-host
check:
	uv tool run black --check --diff $(FILES)
	uv tool run isort --check --diff $(FILES)
	uv tool run ruff check $(FILES)
	. .venv/bin/activate; python -m mypy --strict $(FILES)
	# Configuration check. TOML lib needs Python 3.12. Ignoring errors for now.
	- . .venv/bin/activate; python -m hil.configuration

.PHONY: fix
fix:
	uv tool run black $(FILES)
	uv tool run isort $(FILES)
	uv tool run ruff --fix $(FILES)

FW=bin/lpc55-v1.5.0
MODEL=lpc55
SETUP_LOG=artifacts/setup.log
LOCAL ?= false
ci:
	mkdir -p artifacts
	uv venv --python "$(PYTHON)"
	uv pip install -r requirements.txt
	# TODO: once uv implements its run / exec command, use that
	. .venv/bin/activate; python main.py --verbose true --config_file config/$(MODEL)/config.toml --tests $(TESTS) --local $(LOCAL)

.PHONY: ci-setup-ubuntu
ci-setup-ubuntu:
	apt update
	apt install -qy git make python3.12 python3-pip
	pip install uv --break-system-packages
	uv venv --python "$(PYTHON)"
	uv pip install -r dev-requirements.txt

_local:
	-git clone --recursive https://github.com/Nitrokey/nitrokey-3-firmware.git nitrokey-3-firmware
	cp -r nitrokey-3-firmware/utils ..
	make ci LOCAL=true

ifeq (${DOCKER}, podman)
SEC_OPTS = --security-opt seccomp=unconfined
endif
run_local: build_local
	nitropy nk3 list | grep -v :: | wc -l | awk '$$1 != "1" {print "ERR:\tYou have " $$1 " nk3 devices connected\nINFO:\tConnect exactly 1 nk3 device and retry"; exit 2}'
	$(DOCKER) run -d $(SEC_OPTS) --privileged -it --rm --name nk3-local-hw-test -v /dev:/dev:rw -v ./artifacts:/home/nk3test/artifacts local-hardware-test:latest
	$(DOCKER) cp . nk3-local-hw-test:/home/nk3test/nitrokey-hardware-test
	nitropy nk3 status | grep NRF52 && $(DOCKER) exec nk3-local-hw-test make -C /home/nk3test/nitrokey-hardware-test _local FW=../artifacts MODEL=nrf52 TESTS=$(TESTS) PYTHON=$(PYTHON) || true
	nitropy nk3 status | grep LPC55 && $(DOCKER) exec nk3-local-hw-test make -C /home/nk3test/nitrokey-hardware-test _local FW=../artifacts MODEL=lpc55 TESTS=$(TESTS) PYTHON=$(PYTHON) || true
	$(DOCKER) stop nk3-local-hw-test

build_local:
	$(DOCKER) build $(SEC_OPTS) . --pull -t local-hardware-test:latest -f docker/Dockerfile-local

glab-runner:
	# This runs the Gitlab runner locally for nitrokey-hardware-test CI. Needs to be registered first before accepting jobs. See Readme.md for the details.
	podman build docker/ -t glab-runner-fedora -f docker/Dockerfile-runner
	podman run -it --rm -v gitlab-runner-config:/etc/gitlab-runner -v /dev:/dev:rw --privileged --group-add keep-groups --name nk3-tests glab-runner-fedora:latest

glab-runner-nk3:
	# This runs the Gitlab runner locally for Nitrokey 3 Firmware CI. Needs to be registered first before accepting jobs. See Readme.md for the details.
	podman build docker/ -t glab-runner-fedora -f docker/Dockerfile-runner
	podman run -it --rm -v gitlab-runner-config-nk3:/etc/gitlab-runner -v /dev:/dev:rw --privileged --group-add keep-groups --name nk3-main-repo glab-runner-fedora:latest

NKTESTUSER=nk3tests
setup-fedora-host:
	# Install udev rules for NK3's, debug adapters and YKUSH
	sudo cp docker/41-nitrokey-test.rules /etc/udev/rules.d/
	sudo udevadm control --reload-rules && sudo udevadm trigger
	# Install Web Console
	sudo dnf install cockpit -y
	# TODO check if following is needed
	sudo systemctl enable --now cockpit.socket
	# Set up Podman images autoupdate daily
	# https://fedoramagazine.org/auto-updating-podman-containers-with-systemd/
	systemctl enable --now podman-auto-update.timer
	# https://linuxiac.com/how-to-set-up-automatic-updates-on-fedora-linux/
	sudo dnf install dnf-automatic -y
	# make only security updates; set to "default" to have all
	sudo sed -i 's|upgrade_type = default|upgrade_type = security|g' /etc/dnf/automatic.conf
	sudo sed -i 's|apply_updates = no|apply_updates = yes|g' /etc/dnf/automatic.conf
	# default is to never reboot
	#sudo sed -i 's|reboot = never|reboot = when-needed|g' /etc/dnf/automatic.conf
	# Configure container autostart:
	# - https://www.redhat.com/sysadmin/container-systemd-persist-reboot
	#sudo useradd $(NKTESTUSER)
	#sudo passwd $(NKTESTUSER)
	$(MAKE) setup-fedora-host-user-pre

setup-fedora-host-user-pre:
	sudo adduser --disabled-password --shell /bin/bash $(NKTESTUSER)
	# This command will ensure that a user session for your user is spawned at boot and kept active even after logouts from GUI or tty session(s).
	sudo loginctl enable-linger $(NKTESTUSER)
	# Prepare to run as another user. Copy needed files to the tmp dir.
	mkdir -p /tmp/$(NKTESTUSER) /tmp/$(NKTESTUSER)/bin
	cp -rf Makefile  ./docker /tmp/$(NKTESTUSER)
	cp -rf docker/nk3-tests.container /tmp/$(NKTESTUSER)/bin/
	cd /tmp/$(NKTESTUSER)/ && sudo -s -u $(NKTESTUSER) make setup-fedora-host-user

setup-fedora-host-user:
	# All these should be run from under $(NKTESTUSER) id
	mkdir -p ~$(NKTESTUSER)/.config/containers/systemd/
	cp -Z docker/nk3-tests.container  ~$(NKTESTUSER)/.config/containers/systemd/
	#sudo chown $(NKTESTUSER):$(NKTESTUSER) -R ~$(NKTESTUSER)/.config/systemd/user/
	# Done. Let's run it.
	podman build docker/ -t glab-runner-fedora:latest -f docker/Dockerfile-runner
	# - podman kill nk3-tests
	systemctl --user daemon-reload
	systemctl --user start nk3-tests.service
	systemctl --user status nk3-tests.service

gl-runner-enter:
	sudo -s -u $(NKTESTUSER) podman exec -it nk3-tests bash

gl-runner-start:
	sudo -s -u $(NKTESTUSER) systemctl --user daemon-reload
	sudo -s -u $(NKTESTUSER) systemctl --user start nk3-tests.service

gl-runner-status:
	sudo -s -u $(NKTESTUSER) systemctl --user status nk3-tests.service

gl-runner-stop:
	sudo -s -u $(NKTESTUSER) systemctl --user stop nk3-tests.service

clean-setup-fedora-host:
	# TODO (if needed)
	# remove user and home directory
	userdel -r $(NKTESTUSER)
	# remove linger
	# remove image, volume and containers
