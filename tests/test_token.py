import ape
from pytest import raises


def test_initial_state(token, owner):
    """
    Test inital state of the contract.
    """
    # Check the token meta matches the deployment
    # token.method_name() has access to all the methods in the smart contract.
    assert token.name() == "Cloud AUD"
    assert token.symbol() == "CAUD"
    assert token.decimals() == 8

    # Check of intial state of authorization
    assert token.owner() == owner

    # Check intial balance of tokens
    token.mint(owner, 1000, sender=owner)
    assert token.totalSupply() == 1000
    assert token.balanceOf(owner) == 1000


def test_transfer(token, owner, receiver):
    """
    Transfer must transfer an amount to an address.
    Must trigger Transfer Event.
    Should throw an error of balance if sender does not have enough funds.
    """
    token.mint(owner, 1000, sender=owner)
    owner_balance = token.balanceOf(owner)
    assert owner_balance == 1000

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 0

    # token.method_name() has access to all the methods in the smart contract.
    tx = token.transfer(receiver, 100, sender=owner)

    # validate that Transfer Log is correct
    # https://docs.apeworx.io/ape/stable/methoddocs/api.html?highlight=decode#ape.api.networks.EcosystemAPI.decode_logs
    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 1
    assert logs[0].sender == owner
    assert logs[0].receiver == receiver
    assert logs[0].amount == 100

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 100

    owner_balance = token.balanceOf(owner)
    assert owner_balance == 900

    # Expected insufficient funds failure
    # ape.reverts: Reverts the current call using a given snapshot ID.
    # Allows developers to go back to a previous state.
    # https://docs.apeworx.io/ape/stable/methoddocs/api.html?highlight=revert
    with ape.reverts():
        token.transfer(owner, 200, sender=receiver)

    # NOTE: Transfers of 0 values MUST be treated as normal transfers
    # and trigger a Transfer event.
    tx = token.transfer(owner, 0, sender=owner, max_fee="1000 gwei", max_priority_fee="1000 gwei")

    print("test_transfer print happened!")
    logs = list(tx.decode_logs(token.GasRemaining))
    for ev in logs:
        print("GasRemaining = %s." % ev.gas_remaining)


def test_transfer_from(token, owner, accounts):
    """
    Transfer tokens to an address.
    Transfer operator may not be an owner.
    Approve must be valid to be a spender.
    """
    receiver, spender = accounts[1:3]

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

    # With auth use the allowance to send to receiver via spender(operator)
    tx = token.transferFrom(owner, receiver, 200, sender=spender)

    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 1
    assert logs[0].sender == owner
    assert logs[0].receiver == receiver
    assert logs[0].amount == 200

    assert token.allowance(owner, spender) == 100

    # Cannot exceed authorized allowance
    with ape.reverts():
        token.transferFrom(owner, receiver, 200, sender=spender)

    token.transferFrom(owner, receiver, 100, sender=spender)
    assert token.balanceOf(spender) == 0
    assert token.balanceOf(receiver) == 300
    assert token.balanceOf(owner) == 700


def test_approve(token, owner, receiver):
    """
    Check the authorization of an operator(spender).
    Check the logs of Approve.
    """
    spender = receiver

    tx = token.approve(spender, 300, sender=owner)

    logs = list(tx.decode_logs(token.Approval))
    assert len(logs) == 1
    assert logs[0].owner == owner
    assert logs[0].spender == spender
    assert logs[0].amount == 300

    assert token.allowance(owner, spender) == 300

    # Set auth balance to 0 and check attacks vectors
    # though the contract itself shouldn’t enforce it,
    # to allow backwards compatibility
    tx = token.approve(spender, 0, sender=owner)

    logs = list(tx.decode_logs(token.Approval))
    assert len(logs) == 1
    assert logs[0].owner == owner
    assert logs[0].spender == spender
    assert logs[0].amount == 0

    assert token.allowance(owner, spender) == 0


def test_mint(token, owner, receiver, ZERO_ADDRESS):
    """
    Create an approved amount of tokens.
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


def test_burn(token, owner):
    """
    Burn, i.e. send amount of tokens to ZERO Address.
    """
    token.mint(owner, 1000, sender=owner)
    totalSupply = token.totalSupply()
    assert totalSupply == 1000

    owner_balance = token.balanceOf(owner)
    assert owner_balance == 1000

    tx = token.burn(420, sender=owner)

    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 1
    assert logs[0].sender == owner
    assert logs[0].amount == 420

    owner_balance = token.balanceOf(owner)
    assert owner_balance == 580

    totalSupply = token.totalSupply()
    assert totalSupply == 580


def test_burn_invalid_amount(token, owner):
    """
    Try to burn more tokens than owned.
    """
    token.mint(owner, 50, sender=owner)
    totalSupply = token.totalSupply()
    assert totalSupply == 50

    with raises(ape.exceptions.ContractLogicError):
        token.burn(420, sender=owner)
