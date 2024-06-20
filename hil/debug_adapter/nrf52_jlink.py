from typing import Optional

from hil.debug_adapter.debug_adapter import DebugAdapter
from hil.test_configuration import ExistingFilePath


class JLink(DebugAdapter):
    def erase_and_flash(self, firmware: ExistingFilePath) -> None:
        pass

    def reboot(self) -> bool:
        self.runner("nrfjprog -f NRF52 --reset")
        return True

    def erase_and_flash_bootloader(
        self, mbr: ExistingFilePath, bootloader: ExistingFilePath
    ) -> None:
        self.runner("nrfjprog -f NRF52 --recover")
        self.runner("nrfjprog -f NRF52 --eraseall")
        self.runner(
            f"nrfjprog -f NRF52 --program {mbr.path_str} --sectorerase --verify"
        )
        self.runner(
            f"nrfjprog -f NRF52 --program {bootloader.path_str} --sectorerase --verify"
        )

        # UICR:REGOUT0 to 3v3
        self.runner("nrfjprog -f NRF52 --memwr 0x10001304 --val 0xfffffffd --verify")
        # UICR:NFCPINS to disabled
        self.runner("nrfjprog -f NRF52 --memwr 0x1000120C --val 0xfffffffe --verify")

        # don't set APPROTECT

    def erase(self) -> None:
        cmd = "nrfjprog -f NRF52 --recover"
        self.runner(cmd)

    def flash_firmware(
        self, firmware_path: str, serial_port: Optional[str] = None
    ) -> None:
        hw = "52"
        sd_version = "0x0"
        key_path = self.cfg.bootloader_key.path_str
        app_version = "1234"
        outfile = "fw-temp.zip"

        cmd = f"nrfutil pkg generate --hw-version {hw} --application-version {app_version} "
        cmd += f"--application {firmware_path} --sd-req {sd_version} --key-file {key_path} "
        cmd += f"--app-boot-validation VALIDATE_ECDSA_P256_SHA256 {outfile}"

        self.runner(cmd)

        cmd = f"nrfutil dfu usb-serial -pkg {outfile} -p {serial_port}"
        self.runner(cmd)
