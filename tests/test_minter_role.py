import ape
import pytest


def test_transfer_minter(token, owner, receiver):
    """
    Tests succesful transfer of minter role.
    """
    assert token.minter() == owner

    token.transferMinter(receiver, sender=owner)
    assert token.minter() == receiver
    assert token.minter() != owner

    # test that old minter can no longer mint
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.mint(owner, 100, sender=owner)
    assert exc_info.value.args[0] == "Access denied."
    assert token.balanceOf(owner) == 0

    # test that the new minter can mint
    token.mint(receiver, 100, sender=receiver)
    assert token.balanceOf(receiver) == 100


def test_transfer_minter_targeting_zero_address(token, owner, ZERO_ADDRESS):
    """
    Tests transferring minter role to ZERO_ADDRESS.
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.transferMinter(ZERO_ADDRESS, sender=owner)
    assert exc_info.value.args[0] == "Cannot add null address as minter."


def test_transfer_invalid_access(token, accounts):
    """
    Tests transferring minter role from a non-owner address.
    """
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.transferMinter(accounts[2], sender=accounts[2])
    assert exc_info.value.args[0] == "Access denied."

    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.transferMinter(accounts[5], sender=accounts[3])
    assert exc_info.value.args[0] == "Access denied."
