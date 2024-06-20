from hil.provisioner.provision import Provisioner


class ProvisionerSolo(Provisioner):
    """Provision using solo2 tool
    Note: this was not tested."""

    def get_solo(self, name: str) -> str:
        SOLO2 = './bin/tools/solo2 --name "{}" app provisioner '
        return SOLO2.format(name)

    def provision(self) -> None:
        assert self.cfg.device_id
        name = self.get_solo(self.cfg.device_id)
        cmds = [
            f"{name} write-file {self.cfg.fido_certificate_path} fido/x5c/00",
            f"{name} write-file {self.cfg.fido_key_path} fido/sec/00",
        ]
        for cmd in cmds:
            self.runner(cmd)
