from typing import List

from hil.test_suites.test_suite import TestResult, TestSuite


class SecretsFullTestSuite(TestSuite):
    """Runner for the Secrets Test Suite"""

    def get_artifacts_list(self) -> List[str]:
        return [
            "tests/nitrokey-3-tests/report-secrets-full.html",
            "tests/nitrokey-3-tests/report-junit-secrets-full.xml",
        ]

    def execute(self, uuid: str) -> TestResult:
        cmds = """
        make -C tests/nitrokey-3-tests run-extra-secrets-tests-slow DOCKER=podman ALLOWED_UUIDS={uuid} << EOF
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
