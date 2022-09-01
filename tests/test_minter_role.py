#!/usr/bin/env python3.8
import ape
import pytest

# consts
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

def test_add_minter(token, owner, accounts):
    """
    Test adding new minter.
    Must trigger MinterAdded Event.
    Must return true when checking if target isMinter
    """
    target = accounts[1] 
    token.addMinter(target, sender=owner)
    assert token.isMinter(target) == True

def test_add_minter_targeting_zero_address(token, owner):
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

def test_remove_minter_targeting_zero_address(token, owner):
    """
    Test removing address from minter role targeting ZERO_ADDRESS
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = ZERO_ADDRESS
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.removeMinter(target, sender=owner)
    assert exc_info.value.args[0] == "Targeted address is not a minter"
