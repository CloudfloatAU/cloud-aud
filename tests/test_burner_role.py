#!/usr/bin/env python3.8
import ape
import pytest


def test_add_burner(token, owner, accounts):
    """
    Test adding new burner.
    Must trigger MinterAdded Event.
    Must return true when checking if target isBurner
    """
    target = accounts[1]
    token.addBurner(target, sender=owner)
    assert token.isBurner(target) == True


def test_add_burner_targeting_zero_address(token, owner, ZERO_ADDRESS):
    """
    Test adding new burner targeting ZERO_ADDRESS
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = ZERO_ADDRESS
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.addBurner(target, sender=owner)
    assert exc_info.value.args[0] == "Cannot add null address as burner"


def test_remove_burner(token, owner, accounts):
    """
    Test removing address from burner role
    Must return False when checking if target isBurner
    """
    target = accounts[1]
    token.addBurner(target, sender=owner)
    assert token.isBurner(target) == True
    token.removeBurner(target, sender=owner)
    assert token.isBurner(target) == False


def test_remove_burner_targeting_non_burner(token, owner, accounts):
    """
    Test removing address from burner role targeting an previously removed target
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = accounts[1]
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.removeBurner(target, sender=owner)
    assert exc_info.value.args[0] == "Targeted address is not a burner"


def test_remove_burner_targeting_already_removed(token, owner, accounts):
    """
    Test removing address from burner role targeting an previously removed target
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = accounts[1]
    token.addBurner(target, sender=owner)
    assert token.isBurner(target) == True
    token.removeBurner(target, sender=owner)
    assert token.isBurner(target) == False
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.removeBurner(target, sender=owner)
    assert exc_info.value.args[0] == "Targeted address is not a burner"


def test_remove_burner_targeting_zero_address(token, owner, ZERO_ADDRESS):
    """
    Test removing address from burner role targeting ZERO_ADDRESS
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = ZERO_ADDRESS
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.removeBurner(target, sender=owner)
    assert exc_info.value.args[0] == "Targeted address is not a burner"
