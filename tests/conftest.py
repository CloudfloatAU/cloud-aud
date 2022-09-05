import pytest


@pytest.fixture(scope="session")
def owner(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def receiver(accounts):
    return accounts[1]


@pytest.fixture(scope="session")
def token(owner, project):
    return owner.deploy(project.Token)


@pytest.fixture(scope="session")
def ZERO_ADDRESS() -> str:
    """
    Zero / Null Address
    https://consensys.github.io/smart-contract-best-practices/development-recommendations/token-specific/zero-address/

    Returns:
        "0x0000000000000000000000000000000000000000"
    """
    return "0x0000000000000000000000000000000000000000"
