import ape
import pytest


def test_transfer_ownership(token, owner, receiver):
    """
    Test transferring ownership from one address to another.
    """
    assert token.owner() == owner
    token.mint(owner, 1000, sender=owner)
    assert token.balanceOf(owner) == 1000

    # transfer ownership to received
    token.transferOwnership(receiver, sender=owner)
    assert token.owner() != owner
    assert token.owner() == receiver

    # test that owner can no longer mint
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.mint(owner, 100, sender=owner)
    assert exc_info.value.args[0] == "Access denied."

    # test that the new owner can mint
    token.mint(receiver, 101, sender=receiver)
    assert token.balanceOf(receiver) == 101
