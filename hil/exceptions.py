class HILExceptions(Exception):
    pass


class DeprecatedException(HILExceptions):
    pass


class NoDeviceDetectedException(HILExceptions):
    pass


class RunnerCommandFailedException(HILExceptions):
    pass
