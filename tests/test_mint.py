import ape
import pytest


def test_mint(token, owner, receiver, ZERO_ADDRESS):
    """
    Tests minting new tokens.
    """
    token.mint(owner, 1000, sender=owner)
    totalSupply = token.totalSupply()
    assert totalSupply == 1000

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 0

    tx = token.mint(receiver, 420, sender=owner)

    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 1
    assert logs[0].sender == ZERO_ADDRESS
    assert logs[0].receiver == receiver.address
    assert logs[0].amount == 420

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 420

    totalSupply = token.totalSupply()
    assert totalSupply == 1420


def test_mint_to_zero_address(token, owner, receiver, ZERO_ADDRESS):
    """
    Tests minting new tokens.
    """
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.mint(ZERO_ADDRESS, 100, sender=owner)
        assert exc_info == "Cannot mint to null address."
    assert token.totalSupply() == 0
