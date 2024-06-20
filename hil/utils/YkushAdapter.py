import logging
import sys
import time
import typing
from contextlib import contextmanager
from enum import Enum
from typing import Iterator, List, Optional

import pexpect

logger = logging.getLogger(__name__)


# YKUSH = "ykush/bin/ykushcmd ykush3"
YKUSH = "/usr/bin/ykushcmd ykush3"


class YkushAdapterException(RuntimeWarning):
    pass


class YkushPorts(Enum):
    Port1 = 1
    Port2 = 2
    Port3 = 3
    All = "a"


class YkushDevices(Enum):
    """Map devices to ports, according to the current connections picture"""

    LPC55 = YkushPorts.Port1
    DebugLPC55 = YkushPorts.Port2
    NRF52 = YkushPorts.Port1
    DebugNRF52 = YkushPorts.Port2
    # ThirdModel = YkushPorts.Port3


class YkushState(Enum):
    Active = "u"
    NotActive = "d"


class YkushAdapter(object):
    logger: logging.Logger
    dormant = False
    pathid: Optional[str] = None
    serial: Optional[str] = None

    def __init__(
        self,
        dormant: bool = False,
        pathid: Optional[str] = None,
        serial: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.logger = logger.getChild(f"ykush-{pathid}")
        self.dormant = dormant
        self.pathid = pathid
        self.serial = serial
        self.logger.debug("Initialized")

    def enable_all_ports(self) -> None:
        self.logger.debug("Power up all ports")
        cmd = f"{YKUSH} -u a"
        self._run_command(cmd)
        time.sleep(1)

    def set_port_state(self, port: YkushPorts, state: YkushState) -> None:
        self.logger.debug(f"Set port {port} to state {state}")
        cmd = f"{YKUSH} -{state.value} {port.value}"
        self._run_command(cmd)
        time.sleep(1)

    def disable_all_ports(self) -> None:
        self.logger.debug("Power down all ports")
        cmd = f"{YKUSH} -d a"
        self._run_command(cmd)

    def detect_and_list_boards(self) -> List[str]:
        """
        List boards and get their SN
        :return: a list of SNs of the connected boards
        """
        # Example output:
        """
        $ /usr/bin/ykushcmd ykush3 -l
        Attached YKUSH3 Boards:
        1. Board found with serial number: Y3N11073
        2. Board found with serial number: Y3N110811

        --> ['Y3N11073', 'Y3N110811']
        """
        serial_numbers = []
        self.logger.debug("List devices")
        cmd = f"{YKUSH} -l"
        output = self._run_command(cmd)
        for line in output:
            line = line.strip()
            if not line:
                continue
            if "Board found" in line:
                sn = line.split()[-1]
                serial_numbers.append(sn)
        return serial_numbers

    def disable_other_boards(self) -> None:
        if self.dormant:
            return
        assert self.serial, "Instance has to know its serial number"
        serials = self.detect_and_list_boards()
        for s in serials:
            if s != self.serial:
                adapter = YkushAdapter(self.dormant, serial=s)
                adapter.disable_all_ports()

    # FIXME use runner instead of pexpect?
    def _run_command(self, cmd: str, timeout: int = 5) -> List[str]:
        if self.serial and "-l" not in cmd:
            cmd = cmd.replace("ykush3", f'ykush3 -s "{self.serial}"')

        self.logger.debug(f'Running "{cmd}", timeout {timeout}')
        if self.dormant:
            self.logger.debug("Dormant mode active, not executing")
            return []
        output: str = pexpect.run(cmd, timeout=timeout).decode()
        lines_list = output.splitlines()
        self.logger.debug(f"Results: {lines_list}")
        if "No YKUSH boards found" in output or "Unable to open device" in output:
            raise YkushAdapterException(
                "No YKUSH board found, or cannot connect to one"
            )
        return lines_list

    @contextmanager
    def context_activate_all_on_exit(self) -> Iterator[typing.Any]:
        try:
            yield self
        finally:
            # Make an attempt to power up all ports, ignore errors
            try:
                self.enable_all_ports()
            except Exception:
                self.logger.exception("Failed to enable all ports")


def test_set_port() -> None:
    logging.basicConfig(
        format="* %(relativeCreated)6dms %(filename)s:%(lineno)d %(message)s",
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    k = YkushAdapter(False)

    from unittest.mock import MagicMock

    k._run_command = MagicMock(return_value=[])  # type: ignore[method-assign]

    k.set_port_state(YkushPorts.All, YkushState.NotActive)
    k._run_command.assert_called_with(f"{YKUSH} -d a")

    k.set_port_state(YkushPorts.Port1, YkushState.Active)
    k._run_command.assert_called_with(f"{YKUSH} -u 1")

    k.set_port_state(YkushPorts.Port2, YkushState.Active)
    k._run_command.assert_called_with(f"{YKUSH} -u 2")

    k.set_port_state(YkushPorts.Port3, YkushState.NotActive)
    k._run_command.assert_called_with(f"{YKUSH} -d 3")


def test_ykush() -> None:
    logging.basicConfig(
        format="* %(relativeCreated)6dms %(filename)s:%(lineno)d %(message)s",
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    k = YkushAdapter(False)
    k.detect_and_list_boards()
    time.sleep(1)
    k.disable_all_ports()
    time.sleep(1)
    k.enable_all_ports()
    time.sleep(1)
    k.disable_all_ports()
