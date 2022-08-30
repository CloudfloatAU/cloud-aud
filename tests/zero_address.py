#!/usr/bin/env python3.8
import ape
import pytest

# Standard test comes from the interpretation of EIP-20
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

def test_transfer_to_zero_address(token, owner):
    """
    Transfer must not transfer an amount to a zero address.
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    token.mint(owner, 1000, sender=owner)
    owner_balance = token.balanceOf(owner)
    assert owner_balance == 1000

    receiver = ZERO_ADDRESS
    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 0

    # token.method_name() has access to all the methods in the smart contract.
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
      token.transfer(receiver, 100, sender=owner)

    assert exc_info.value.args[0] == "Cannot transfer to null address"
