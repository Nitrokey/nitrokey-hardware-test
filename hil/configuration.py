from hil.test_configuration import ExistingFilePath, TestConfiguration

# TODO: move to yaml/pydantic instead?
# https://docs.pydantic.dev/latest/
# https://pypi.org/project/dataclasses-serialization/
# https://pypi.org/project/serde/
# https://pypi.org/project/pyserde/


def get_configuration() -> TestConfiguration:
    return TestConfiguration.from_config_file(ExistingFilePath("config.toml"))


if __name__ == "__main__":
    cfg = get_configuration()
    print(cfg)
