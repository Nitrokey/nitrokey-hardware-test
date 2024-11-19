import dataclasses
import logging
import subprocess
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence

from hil.exceptions import RunnerCommandFailedException

DEFAULT_SUBPROCESS_TIMEOUT = 1800

log = logging.getLogger(__name__)


@dataclasses.dataclass
class Runner(ABC):
    err_strings: Sequence[bytes] = dataclasses.field(
        default_factory=lambda: [b"Error", b"FAILED", b"FAILURE"]
    )

    @abstractmethod
    def __call__(
        self,
        cmd: str,
        timeout: Optional[int] = None,
        save_output_to: Optional[str] = None,
    ) -> str: ...

    @abstractmethod
    def call_with_timeout(self, cmd: str, timeout: int) -> str: ...


class CheckRunner(Runner):
    def runner(
        self,
        cmd: str,
        save_output_to: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> str:
        if timeout is None:
            timeout = DEFAULT_SUBPROCESS_TIMEOUT
        cmd = cmd.strip()
        run_in_shell = "EOF" in cmd
        # run_in_shell = False
        cmd_final = cmd if run_in_shell else cmd.split()
        log.debug(f"Calling (timeout: {timeout}): {cmd_final}")
        # TODO replace check_output with non-blocking popen, and show progress/last line
        try:
            res = subprocess.check_output(
                cmd_final,
                timeout=timeout,
                shell=run_in_shell,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as e:
            res = e.output

        def uniq(lines: List[bytes]) -> List[bytes]:
            res = [b""]
            for line in lines:
                if line != res[-1]:
                    res.append(line)
            return res[1:]

        def remove_clutter(lines: List[bytes]) -> List[bytes]:
            res = []
            for line in lines:
                line = line.replace(b"\x08", b"")
                res.append(line)
            return res

        try:
            res_lines = uniq(res.split(b"\n"))
            res_lines = remove_clutter(res_lines)
        except Exception:
            log.exception("Failed to process log lines")
            res_lines = [res]
        log.debug(res_lines)
        if save_output_to:
            with open(save_output_to, "bw+") as f:
                f.write(res)
        for err_str in self.err_strings:
            if err_str in res:
                raise RunnerCommandFailedException(f"Error in execution: {res!r}")

        return res.decode("ascii")

    def __call__(
        self,
        cmd: str,
        timeout: Optional[int] = None,
        save_output_to: Optional[str] = None,
    ) -> str:
        return self.runner(cmd, save_output_to, timeout)

    def call_with_timeout(self, cmd: str, timeout: int) -> str:
        return self.runner(cmd, timeout=timeout)
