import ape
import pytest


def test_transfer_ownership(token, owner, receiver):
    """
    Tests transferring ownership from owner address to another then mint by original
    owner address.
    Must trigger a ContractLogicError when minting post ownership transfer.
    """
    assert token.owner() == owner
    token.mint(owner, 1000, sender=owner)
    assert token.balanceOf(owner) == 1000

    # transfer ownership to receiver
    receipt = token.transferOwnership(receiver, sender=owner)
    assert token.owner() != owner
    assert token.owner() == receiver

    # ensure OwnershipTransfer event was emitted
    logs = receipt.decode_logs(token.OwnershipTransfer)
    assert len(list(logs)) == 1
    for log in logs:
        assert log.previousOwner == owner
        assert log.newOwner == receiver
    del logs, receipt

    # test that new owner cannot mint
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.mint(receiver, 100, sender=receiver)
    assert exc_info.value.args[0] == "Access denied."

    # test that old owner can still mint
    token.mint(receiver, 42, sender=owner)
    assert token.balanceOf(receiver) == 42


def test_transfer_ownership_by_non_owner(token, owner, receiver):
    """
    Test transferring ownership from non-owner to owner address.
    Must trigger an ape.exceptions.ContractLogicError
    Contract owner must remain unchanged.
    """
    assert token.owner() == owner
    token.mint(owner, 1000, sender=owner)
    assert token.balanceOf(owner) == 1000

    # Attempt to transfer ownership
    non_owner = receiver
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.transferOwnership(owner, sender=non_owner)
    assert exc_info.value.args[0] == "Access denied."

    # Ownership remains unchanged
    assert token.owner() == owner


def test_transfer_ownership_to_zero_address(token, owner, ZERO_ADDRESS):
    """
    Test transferring ownership of contract from original owner to a zero address.
    Must trigger an ape.exceptions.ContractLogicError when trasferOwnership is called.
    Contract owner must remain unchanged.
    """
    assert token.owner() == owner
    token.mint(owner, 1000, sender=owner)
    assert token.balanceOf(owner) == 1000

    # Attempt to transfer ownership
    new_owner = ZERO_ADDRESS
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.transferOwnership(new_owner, sender=owner)
    assert exc_info.value.args[0] == "Cannot add null address as owner."

    # Ownership remains unchanged
    assert token.owner() == owner
