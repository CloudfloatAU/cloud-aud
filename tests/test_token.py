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
    assert token.minter() == owner

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
    tx = token.transfer(
        owner,
        0,
        sender=owner,
        gas="200000",
        max_fee="1000 gwei",
        max_priority_fee="1000 gwei",
    )


def test_batch_transfer(token, owner, accounts):
    token.mint(owner, 1000, sender=owner)
    payments = []

    # Record starting balances of all accounts.
    starting_balances = []
    starting_balances.append(token.balanceOf(accounts[0]))
    for i in range(9):
        payments.append((accounts[i + 1], 1))
        starting_balances.append(token.balanceOf(accounts[i + 1]))

    tx = token.batchTransfer(payments, sender=owner, gas="1000000")
    assert tx.failed is False

    # Compare pre/post tx balances for all accounts.
    assert starting_balances[0] == token.balanceOf(accounts[0]) + 9
    for i in range(9):
        assert starting_balances[i + 1] == token.balanceOf(accounts[i + 1]) - 1

    logs = list(tx.decode_logs(token.Transfer))
    print("Logs[%s] = %s." % (len(logs), logs))

    logs = list(tx.decode_logs(token.BatchTransfer))
    print("Logs[%s] = %s." % (len(logs), logs))

    event = logs[0]

    print("GasExhausted = %s." % event.gas_exhausted)
    print("GasPerTx = %s." % event.gas_per_tx)
    assert event.gas_exhausted is False
    assert event.tx_count == 9
    assert event.tx_value == 9

    assert tx.ran_out_of_gas is False


def test_batch_transfer_exhaust_min_gas_remaining(token, owner, accounts):
    token.mint(owner, 1000, sender=owner)
    payments = []
    for i in range(9):
        payments.append((accounts[i + 1], 1))

    # Token.vy assumptions:
    # MIN_GAS_REMAINING == 30,000
    # EST_GAS_PER_TRANSFER == 29000

    # 40,000 gas will get the tx started but abort on the first one.
    tx = token.batchTransfer(payments, sender=owner, gas="40000")
    assert tx.failed is False

    logs = list(tx.decode_logs(token.BatchTransfer))

    assert logs[0].gas_exhausted is True
    assert logs[0].tx_count == 0
    assert logs[0].tx_value == 0

    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 0

    assert tx.ran_out_of_gas is False


def test_batch_transfer_partial_batch_only(token, owner, accounts):
    token.mint(owner, 1000, sender=owner)
    payments = []
    for i in range(9):
        payments.append((accounts[i + 1], 1))

    # Token.vy assumptions:
    # MIN_GAS_REMAINING == 30,000
    # EST_GAS_PER_TRANSFER == 29000

    # 120,000 gas will get the tx started but abort after the second one.
    tx = token.batchTransfer(payments, sender=owner, gas="120000")
    assert tx.failed is False

    logs = list(tx.decode_logs(token.BatchTransfer))

    assert logs[0].gas_exhausted is True
    assert logs[0].tx_count == 2
    assert logs[0].tx_value == 2

    logs = list(tx.decode_logs(token.Transfer))
    print("Transfer Logs[%s] = %s." % (len(logs), logs))
    assert len(logs) == 2

    assert tx.ran_out_of_gas is False


def test_batch_transfer_insufficient_funds(token, owner, accounts):
    # owner only has two tokens to transfer! Should only complete one tx.
    token.mint(owner, 2, sender=owner)
    payments = []
    for i in range(9):
        payments.append((accounts[i + 1], 2))

    print("Owner balance: %s." % token.balanceOf(owner))

    tx = token.batchTransfer(payments, sender=owner, gas="10000000")

    assert tx.failed is False

    logs = list(tx.decode_logs(token.BatchTransfer))

    print("BatchTransfer logs: %s", logs)
    assert logs[0].gas_exhausted is False
    assert logs[0].tx_count == 1
    assert logs[0].tx_value == 2

    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 1
    print("Transfer Logs[%s] = %s." % (len(logs), logs))

    print("Owner balance: %s." % token.balanceOf(owner))

    assert tx.ran_out_of_gas is False


def test_batch_larger_than_max_size(token, owner, accounts):
    token.mint(owner, 1000, sender=owner)

    # Assumes MAX_PAYMENTS == 200
    payments = []
    for i in range(201):
        payments.append((accounts[(i % 9) + 1], 1))

    # with ape.reverts():
    tx = token.batchTransfer(payments, sender=owner, gas="1000000")

    assert tx.failed is True

    # print(token.raise_for_status())

    # logs = list(tx.decode_logs(token.Transfer))
    # print("Logs[%s] = %s." %(len(logs),logs))
    # print("%s transfers!" % len(logs))

    # logs = list(tx.decode_logs(token.BatchTransfer))
    # print("Logs[%s] = %s." %(len(logs),logs))


def test_batch_transfer_aborts_when_hits_zero_address(
    token, owner, accounts, ZERO_ADDRESS
):
    token.mint(owner, 1000, sender=owner)
    payments = []
    for i in range(9):
        payments.append((accounts[i + 1], 1))

    # Change the 4th tx to go to address 0.
    payments[3] = (ZERO_ADDRESS, 1)

    tx = token.batchTransfer(payments, sender=owner, gas="1000000")
    assert tx.failed is False

    logs = list(tx.decode_logs(token.Transfer))
    print("Logs[%s] = %s." % (len(logs), logs))

    logs = list(tx.decode_logs(token.BatchTransfer))
    print("Logs[%s] = %s." % (len(logs), logs))

    event = logs[0]

    print("GasExhausted = %s." % event.gas_exhausted)
    print("GasPerTx = %s." % event.gas_per_tx)
    assert event.gas_exhausted is False
    assert event.tx_count == 3
    assert event.tx_value == 3

    assert tx.ran_out_of_gas is False


def test_gas_savings_vs_token_transfer(token, owner, accounts):
    token.mint(owner, 1000, sender=owner)

    tx_transfer1 = token.transfer(accounts[1], 1, sender=owner, gas="1000000")
    tx_batch1 = token.batchTransfer([(accounts[2], 1)], sender=owner, gas="1000000")

    tx_transfer2 = token.transfer(accounts[3], 1, sender=owner, gas="1000000")
    tx_batch2 = token.batchTransfer(
        [(accounts[4], 1), (accounts[5], 1)], sender=owner, gas="1000000"
    )

    tx_transfer3 = token.transfer(accounts[6], 1, sender=owner, gas="1000000")
    tx_batch3 = token.batchTransfer(
        [(accounts[7], 1), (accounts[8], 1), (accounts[9], 1)],
        sender=owner,
        gas="1000000",
    )

    print(
        "First Single tx: transfer: %s, batchTransfer:%s, delta:%s"
        % (
            tx_transfer1.gas_used,
            tx_batch1.gas_used,
            tx_transfer1.gas_used - tx_batch1.gas_used,
        )
    )
    print(
        "First Double tx: transfer: %s, batchTransfer:%s, delta:%s"
        % (
            tx_transfer1.gas_used + tx_transfer2.gas_used,
            tx_batch2.gas_used,
            (tx_transfer1.gas_used + tx_transfer2.gas_used) - tx_batch2.gas_used,
        )
    )
    print(
        "First Triple tx: transfer: %s, batchTransfer:%s, delta:%s"
        % (
            tx_transfer1.gas_used + tx_transfer2.gas_used + tx_transfer3.gas_used,
            tx_batch3.gas_used,
            (tx_transfer1.gas_used + tx_transfer2.gas_used + tx_transfer3.gas_used)
            - tx_batch3.gas_used,
        )
    )

    assert tx_transfer1.failed is False
    assert tx_transfer2.failed is False
    assert tx_transfer3.failed is False
    assert tx_batch1.failed is False
    assert tx_batch2.failed is False
    assert tx_batch3.failed is False

    tx_transfer1 = token.transfer(accounts[1], 1, sender=owner, gas="1000000")
    tx_batch1 = token.batchTransfer([(accounts[2], 1)], sender=owner, gas="1000000")

    tx_transfer2 = token.transfer(accounts[3], 1, sender=owner, gas="1000000")
    tx_batch2 = token.batchTransfer(
        [(accounts[4], 1), (accounts[5], 1)], sender=owner, gas="1000000"
    )

    tx_transfer3 = token.transfer(accounts[6], 1, sender=owner, gas="1000000")
    tx_batch3 = token.batchTransfer(
        [(accounts[7], 1), (accounts[8], 1), (accounts[9], 1)],
        sender=owner,
        gas="1000000",
    )

    print(
        "Redo Single tx: transfer: %s, batchTransfer:%s, delta:%s"
        % (
            tx_transfer1.gas_used,
            tx_batch1.gas_used,
            tx_transfer1.gas_used - tx_batch1.gas_used,
        )
    )
    print(
        "Redo Double tx: transfer: %s, batchTransfer:%s, delta:%s"
        % (
            tx_transfer1.gas_used + tx_transfer2.gas_used,
            tx_batch2.gas_used,
            (tx_transfer1.gas_used + tx_transfer2.gas_used) - tx_batch2.gas_used,
        )
    )
    print(
        "Redo Triple tx: transfer: %s, batchTransfer:%s, delta:%s"
        % (
            tx_transfer1.gas_used + tx_transfer2.gas_used + tx_transfer3.gas_used,
            tx_batch3.gas_used,
            (tx_transfer1.gas_used + tx_transfer2.gas_used + tx_transfer3.gas_used)
            - tx_batch3.gas_used,
        )
    )

    assert tx_transfer1.failed is False
    assert tx_transfer2.failed is False
    assert tx_transfer3.failed is False
    assert tx_batch1.failed is False
    assert tx_batch2.failed is False
    assert tx_batch3.failed is False

    payments = []
    for i in range(100):
        payments.append((accounts[(i % 9) + 1], 1))

    tx_batch100 = token.batchTransfer(payments, sender=owner, gas="1000000")
    print(
        "Redo 100x tx: transfer: %s, batchTransfer:%s, delta:%s"
        % (
            tx_transfer1.gas_used * 100,
            tx_batch100.gas_used,
            (tx_transfer1.gas_used * 100) - tx_batch100.gas_used,
        )
    )

    assert tx_batch100.failed is False


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
