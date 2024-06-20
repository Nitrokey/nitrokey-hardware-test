import dataclasses
import logging
from typing import Sequence

from hil.device.device import Device
from hil.provisioner.provision import ProvisionConfiguration
from hil.provisioner.pynitrokey import ProvisionerPynitrokey
from hil.runner import Runner
from hil.test_configuration import TestConfiguration
from hil.test_suites.test_suite import TestResult, TestSuite

log = logging.getLogger(__name__)


@dataclasses.dataclass
class TestLoop:
    target_device: Device
    provision_configuration: ProvisionConfiguration
    test_suites: Sequence[TestSuite]
    runner: Runner
    test_results: dict[str, TestResult] = dataclasses.field(default_factory=dict)

    def prepare_devices_simulation(self) -> None:
        log.debug("Preparing devices and simulation...")
        # Hardware: Power cycle debug adapter and the target device
        # TODO power off other devices, activate specified slots
        #   on both ykush managers
        self.target_device.erase()
        self.target_device.power_cycle()

    def flash_target_device_provisioner(self, cfg: TestConfiguration) -> None:
        log.debug(f"Flashing target device with software: {cfg}")
        self.target_device.erase_and_flash_bootloader(cfg)
        self.target_device.flash_using_bootloader(cfg.provisioner_firmware.path_str)
        self.target_device.shows_up()

    def flash_target_device_application(self, cfg: TestConfiguration) -> None:
        log.debug(f"Flashing target device with software: {cfg}")
        self.target_device.try_switch_to_bootloader()
        self.target_device.flash_using_bootloader(cfg.application_firmware.path_str)
        self.target_device.shows_up()

    def provision_target_device(self) -> None:
        log.debug("Provisioning target device...")
        self.target_device.provision(
            ProvisionerPynitrokey(self.provision_configuration, self.runner),
        )

    def execute_subtests(self) -> None:
        uuid = self.target_device.uuid()

        for test in self.test_suites:
            self.target_device.power_cycle()
            log.info(f"Executing {test.name()}...")
            self.test_results[test.name()] = test.execute(uuid)
            test.collect_artifacts()

    def get_return_code(self) -> int:
        if any(x.fail() for x in self.test_results.values()):
            return 1
        return 0

    def run_test_loop(self, cfg: TestConfiguration) -> None:
        log.info("Test loop starts")
        self.prepare_devices_simulation()

        log.info("Provisioner stage")
        self.flash_target_device_provisioner(cfg)
        self.provision_target_device()

        log.info("Application stage")
        self.flash_target_device_application(cfg)

        log.info("Executing subtests...")
        self.execute_subtests()

        log.info("Collecting device's state")
        self.download_device_file_system()

        # log.debug(self.test_results)
        # print(self.test_results)
        log.info("Test loop finished")

    def download_device_file_system(self) -> None:
        # Collect file system as an artifact
        # TODO implement download
        pass
