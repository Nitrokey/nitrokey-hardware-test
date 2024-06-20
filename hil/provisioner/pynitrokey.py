from hil.provisioner.provision import Provisioner


class ProvisionerPynitrokey(Provisioner):
    """Provision using pynitrokey"""

    def provision(self) -> None:
        cmd = [
            "nitropy",
            self.cfg.device,
            "provision",
            "fido2",
            "--cert",
            self.cfg.fido_certificate_path.path_str,
            "--key",
            self.cfg.fido_key_path.path_str,
        ]
        cmds = " ".join(cmd)
        self.runner.call_with_timeout(cmds, 10)
