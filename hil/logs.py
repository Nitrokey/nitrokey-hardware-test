import logging
import sys
from pathlib import Path
from typing import TextIO, Tuple

from hil.utils.threaded_log import ThreadLog

LOG_PATH = "artifacts/log.txt"


class HILFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        orig_msg = record.msg
        out = ""

        if isinstance(orig_msg, (list, tuple)):
            record.msg = "Multi-Line Output:"
            out += super().format(record) + "\n"
            for line in orig_msg:
                if isinstance(line, bytes):
                    line = "### " + line.decode()
                record.msg = line
                out += super().format(record) + "\n"
        else:
            out = super().format(record)

        record.msg = orig_msg
        record.message = out

        return out


def get_log_fd(path: str) -> TextIO:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p.open("w+")


def set_logger() -> Tuple[logging.Logger, logging.Handler]:
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    log_file_fd = get_log_fd(LOG_PATH)

    formatter = HILFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handlers = []
    for level, stream in [
        (logging.INFO, sys.stdout),
        (logging.DEBUG, log_file_fd),
    ]:
        handler = logging.StreamHandler(stream)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        log.addHandler(handler)
        handlers.append(handler)

    log.debug(f"Log file path set to {LOG_PATH}")

    nrf_log = logging.getLogger(
        "pynitrokey.nk3.bootloader.nrf52_upload.dfu.dfu_transport_serial"
    )
    for h in nrf_log.handlers:
        nrf_log.removeHandler(h)
    nrf_log.addHandler(handlers[-1])

    return log, handlers[0]


log, console_handler = set_logger()
threaded_system_log = ThreadLog(log.getChild("dmesg"), "dmesg -W")
threaded_system_log.start_logging()
