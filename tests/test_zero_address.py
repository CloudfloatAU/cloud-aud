import ape
import pytest


def test_transfer_to_zero_address(token, owner, ZERO_ADDRESS):
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

    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.transfer(receiver, 100, sender=owner)

    assert exc_info.value.args[0] == "Cannot transfer to null address."


def test_transfer_from_to_zero_address(token, owner, accounts, ZERO_ADDRESS):
    """
    TransferFrom must not transfer tokens to a zero address.
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    receiver, spender = ZERO_ADDRESS, accounts[1]

    token.mint(owner, 1000, sender=owner)
    owner_balance = token.balanceOf(owner)
    assert owner_balance == 1000

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 0

    # Spender with no approve permission cannot send tokens on someone behalf
    with ape.reverts():
        token.transferFrom(owner, receiver, 300, sender=spender)

    # Get approval for allowance from owner
    tx = token.approve(spender, 300, sender=owner)

    logs = list(tx.decode_logs(token.Approval))
    assert len(logs) == 1
    assert logs[0].owner == owner
    assert logs[0].spender == spender
    assert logs[0].amount == 300

    assert token.allowance(owner, spender) == 300

    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        tx = token.transferFrom(owner, receiver, 200, sender=spender)

    assert exc_info.value.args[0] == "Cannot transfer to null address."
