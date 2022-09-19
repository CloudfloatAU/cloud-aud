#!/usr/bin/env python3.8
import ape
import pytest


def test_add_minter(token, owner, accounts):
    """
    Test adding new minter.
    Must trigger MinterAdded Event.
    Must return true when checking if target isMinter
    """
    target = accounts[1]
    token.addMinter(target, sender=owner)
    assert token.isMinter(target) == True


def test_add_minter_targeting_zero_address(token, owner, ZERO_ADDRESS):
    """
    Test adding new minter targeting ZERO_ADDRESS
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = ZERO_ADDRESS
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.addMinter(target, sender=owner)
    assert exc_info.value.args[0] == "Cannot add null address as minter"


def test_remove_minter(token, owner, accounts):
    """
    Test removing address from minter role
    Must return False when checking if target isMinter
    """
    target = accounts[1]
    token.addMinter(target, sender=owner)
    assert token.isMinter(target) == True
    token.removeMinter(target, sender=owner)
    assert token.isMinter(target) == False


def test_remove_minter_targeting_non_minter(token, owner, accounts):
    """
    Test removing address from minter role targeting an previously removed target
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = accounts[1]
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.removeMinter(target, sender=owner)
    assert exc_info.value.args[0] == "Targeted address is not a minter"


def test_remove_minter_targeting_already_removed(token, owner, accounts):
    """
    Test removing address from minter role targeting an previously removed target
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = accounts[1]
    token.addMinter(target, sender=owner)
    assert token.isMinter(target) == True
    token.removeMinter(target, sender=owner)
    assert token.isMinter(target) == False
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.removeMinter(target, sender=owner)
    assert exc_info.value.args[0] == "Targeted address is not a minter"


def test_remove_minter_targeting_zero_address(token, owner, ZERO_ADDRESS):
    """
    Test removing address from minter role targeting ZERO_ADDRESS
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = ZERO_ADDRESS
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.removeMinter(target, sender=owner)
    assert exc_info.value.args[0] == "Targeted address is not a minter"


def test_revoke_minter(token, owner, accounts):
    """
    Test revoking minter role from address granted minter role by owner
    """
    target = accounts[1]
    token.addMinter(target, sender=owner)
    assert token.isMinter(target) == True
    token.revokeMinter(sender=target)
    assert token.isMinter(target) == False


def test_revoke_minter_by_non_minter(token, accounts):
    """
    Test revoking minter role from address never granted minter role
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = accounts[1]
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.revokeMinter(sender=target)
    assert exc_info.value.args[0] == "Sender is not a minter"


def test_revoke_minter(token, owner, accounts):
    """
    Test revoking minter role from address granted minter role by owner, once revoked
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = accounts[1]
    token.addMinter(target, sender=owner)
    assert token.isMinter(target) == True
    token.revokeMinter(sender=target)
    assert token.isMinter(target) == False
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.revokeMinter(sender=target)
    assert exc_info.value.args[0] == "Sender is not a minter"
