from typing import List

from hil.test_suites.test_suite import TestResult, TestSuite


class SecretsTestSuite(TestSuite):
    """Runner for the Secrets Test Suite"""

    def get_artifacts_list(self) -> List[str]:
        return [
            "tests/pynitrokey/report.html",
            "tests/pynitrokey/report-junit.xml",
        ]

    def execute(self, uuid: str) -> TestResult:
        cmds = """
        env FLIT_ROOT_INSTALL=1 make -C tests/pynitrokey/ init DOCKER=podman << EOF 
        make -C tests/pynitrokey/ secrets-test-report-CI DOCKER=podman << EOF
        """.strip()
        err = None
        try:
            for cmd in cmds.splitlines():
                self.runner(cmd)
        except Exception as e:
            err = e
        if err:
            return TestResult([f"Fail: {err}"])
        return TestResult(["OK"])
