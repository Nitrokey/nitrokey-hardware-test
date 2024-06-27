import logging
import sys
import time
from typing import Optional

from hil.debug_adapter.lpc_link import LpcLink
from hil.debug_adapter.nrf52_jlink import JLink
from hil.device.lpc55 import LPC55HardwareDevice
from hil.device.nkpk import NKPKHardwareDevice
from hil.device.nrf52 import NRF52HardwareDevice
from hil.device.usb_power import DummyHubPower, YKushHubPower
from hil.logs import console_handler
from hil.provisioner.provision import ProvisionConfiguration
from hil.runner import CheckRunner
from hil.test_configuration import ExistingFilePath, TestConfiguration
from hil.test_loop import TestLoop
from hil.test_suites.nk3_tests import Nitrokey3TestSuite
from hil.test_suites.pynitrokey_tests import pynitrokeyTestSuite
from hil.test_suites.secrets_full_tests import SecretsFullTestSuite
from hil.test_suites.secrets_tests import SecretsTestSuite

log = logging.getLogger(__name__)


def main(
    application_firmware: Optional[str] = None,
    provisioner_firmware: Optional[str] = None,
    tests: Optional[str] = None,
    device_id: Optional[str] = None,
    config_file: Optional[str] = None,
    verbose: bool = False,
    local: bool = False,
) -> None:
    """
    Nitrokey Hardware Tests

    A hardware test runner, which manages device's flashing and configuration process, runs tests, collects results,
    and gets device's state for the further debugging.

    :param application_firmware: A path to the application firmware
    :param provisioner_firmware: A path to the provisioner firmware
    :param tests: A list of strings for filtering tests by name
    :param device_id: UUID of the device to test
    :param config_file: A path to the configuration file
    :param verbose: Use --verbose true to log DEBUG messages to console
    :param local: Do a local hardware test without ykush (only one nk connected)
    """

    if verbose:
        console_handler.setLevel(logging.DEBUG)
    # TODO: get non-provided parameters from configuration, overridden by env variables
    test_configuration = TestConfiguration.from_config_file(
        ExistingFilePath(config_file if config_file else "config.toml")
    )
    if application_firmware:
        log.debug(f"Setting application firmware to: {application_firmware}")
        test_configuration.application_firmware = ExistingFilePath(application_firmware)
    if provisioner_firmware:
        log.debug(f"Setting provisioner firmware to: {provisioner_firmware}")
        test_configuration.provisioner_firmware = ExistingFilePath(provisioner_firmware)

    prov_configuration = ProvisionConfiguration(
        fido_key_path=test_configuration.fido_key_path,
        fido_certificate_path=test_configuration.fido_certificate_path,
        device=test_configuration.device,
        device_id=device_id,
    )

    # TODO: consider using class names directly in the configuration
    # v2d = {c.__name__: c for c in [NRF52HardwareDevice, LPC55HardwareDevice]}
    v2d = {
        "nrf52": NRF52HardwareDevice,
        "lpc55": LPC55HardwareDevice,
        "nkpk": NKPKHardwareDevice,
    }
    v2da = {"nrf52": JLink, "lpc55": LpcLink, "nkpk": JLink}
    device_cls = v2d[test_configuration.variant]
    debug_adapter_cls = v2da[test_configuration.variant]

    if not local:
        hub_power = YKushHubPower(
            enabled=test_configuration.usb_manager_enabled,
            serial_number=test_configuration.ykush_serial_number,
        )
    else:
        hub_power = DummyHubPower(enabled=True)

    dev = device_cls(  # type: ignore[abstract]
        debug_adapter_cls(CheckRunner(), test_configuration),  # type: ignore[abstract]
        hub_power,
        CheckRunner(),
    )
    hub_power.init()  # TODO move this to factory, or constructor
    time.sleep(5)

    dev.validate_configuration(
        test_configuration
    )  # TODO this should be in constructor as well

    artifacts_destination_path = test_configuration.output

    # use only passed test-suites
    test_suites_map = {
        "pynitrokey": pynitrokeyTestSuite(
            CheckRunner(), artifacts_destination_path, test_configuration
        ),
        "nk3test": Nitrokey3TestSuite(
            CheckRunner(), artifacts_destination_path, test_configuration
        ),
        "secrets": SecretsTestSuite(
            CheckRunner(), artifacts_destination_path, test_configuration
        ),
        "secrets_full": SecretsFullTestSuite(
            CheckRunner(), artifacts_destination_path, test_configuration
        ),
    }
    run_tests = []
    if isinstance(tests, str):
        run_tests = [tests]
    elif isinstance(tests, (list, tuple)):
        run_tests = tests
    test_suites = [v for k, v in test_suites_map.items() if k in run_tests]
    # if none is selected - use pynitrokey only
    if len(test_suites) == 0:
        test_suites = [test_suites_map["pynitrokey"]]

    test_loop = TestLoop(dev, prov_configuration, test_suites, CheckRunner())
    test_loop.run_test_loop(test_configuration)
    log.info("Application finished")
    sys.exit(test_loop.get_return_code())
