from hil.debug_adapter.debug_adapter import DebugAdapter
from hil.runner import Runner
from hil.test_configuration import ExistingFilePath, TestConfiguration


class LpcLink(DebugAdapter):
    def __init__(self, runner: Runner, cfg: TestConfiguration) -> None:
        super().__init__(runner, cfg)
        # FIXME change these only on calling function, instead of changing the defaults
        #   or run clone() first, and then change the new instance
        self.runner.err_strings = [b"Error while programming flash"]

    def erase_and_flash(self, firmware: ExistingFilePath) -> None:
        cmd = f"""
        JLinkExe -device LPC55S69_M33_0 -if SWD -autoconnect 1 -speed 4000 -NoGui 1 -ExitOnError 1 << EOF
        LoadFile {firmware.path_str}
        Reset
        Go"""
        self.runner(cmd)

    def reboot(self) -> bool:
        cmd = """
        JLinkExe -device LPC55S69_M33_0 -if SWD -autoconnect 1 -speed 4000 -NoGui 1 -ExitOnError 1 << EOF
        Reset
        Go"""
        self.runner(cmd)
        return True

    def erase_and_flash_bootloader(
        self, mbr: ExistingFilePath, bootloader: ExistingFilePath
    ) -> None:
        # Nothing to do - bootloader is provided by the vendor, and is immutable
        pass

    def erase(self) -> None:
        cmd = """
        JLinkExe -device LPC55S69_M33_0 -if SWD -autoconnect 1 -speed 4000 -NoGui 1 -ExitOnError 1 << EOF
        erase"""
        self.runner(cmd)
