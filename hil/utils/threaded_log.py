import logging
import subprocess
import threading
import time
from sys import stderr
from typing import List, Sequence


def print_important_info(s: str) -> None:
    pass


class ThreadLog(threading.Thread):
    _asked_to_finish = False
    _dmesg_skip_strings = [b"Audio Port: ASoC", b"RTL8723BS:"]

    _dmesg_warn = [
        b"Device not responding to setup address",
        b"device not accepting address",
        b"unable to enumerate USB device",
    ]

    _write_to_log = False

    def __init__(
        self, logger: logging.Logger, command: str, prefix: bytes = b""
    ) -> None:
        threading.Thread.__init__(self)
        self.logger = logger
        self.command = command
        self.daemon = True
        self.prefix = prefix
        self.start()

    def run(self) -> None:
        self.execute(self.command.split())

    @staticmethod
    def _contains(value: bytes, strings: Sequence[bytes]) -> bool:
        for s in strings:
            if s in value:
                return True
        return False

    def execute(self, command: List[str]) -> None:
        # Poll process for new output until finished
        self.process = subprocess.Popen(
            command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        assert self.process.stdout
        for line in iter(self.process.stdout.readline, ""):
            if self._asked_to_finish:
                break
            if not line or not self._write_to_log:
                continue
            if self._contains(line, self._dmesg_skip_strings):
                continue
            if self._contains(line, self._dmesg_warn):
                print_important_info(
                    f"System reports USB connection error: {line[:80]!r}..."
                )
                self.logger.warning("System reports USB connection error")
                self.logger.warning(self.prefix + line.strip())
                continue
            self.logger.debug(self.prefix + line.strip())

        if self.process.poll() is None:
            self.logger.debug("Killing child process")
            self.process.kill()
        self.logger.debug("Waiting for child process")
        self.process.wait()
        # exitCode = process.returncode

    def start_logging(self) -> None:
        self._write_to_log = True

    def finish(self) -> None:
        self._asked_to_finish = True

    def __del__(self) -> None:
        # TODO check if this deadlocks
        self.finish()
        if self.process.poll() is None:
            self.logger.debug("Killing child process")
            self.process.kill()
        self.logger.debug("Waiting for child process")
        self.process.wait()


def test_run() -> None:
    FORMAT = "%(relativeCreated)05d [%(process)x] - %(levelname)s - %(name)s - %(message)s [%(filename)s:%(lineno)d]"
    logging.basicConfig(format=FORMAT, stream=stderr, level=logging.DEBUG)
    logger = logging.getLogger("threadlog")

    try:
        t = ThreadLog(logger, "dmesg -w")
        time.sleep(10)
        t.finish()
    except (KeyboardInterrupt, SystemExit):
        return
