# @version 0.3.3

"""
@title Bare-bones Token implementation
@notice
    Based on the ERC-20 token standard as defined at
    https://github.com/ethereum/EIPs/issues/20
"""

from vyper.interfaces import ERC20

implements: ERC20

# ERC20 Token Metadata
NAME: constant(String[20]) = "Cloud AUD"
SYMBOL: constant(String[5]) = "CAUD"
DECIMALS: constant(uint8) = 8


MIN_GAS_REMAINING: constant(uint256) = 30000   # Use to reserve remaining gas in case calling from contract that needs to do more things.
MAX_PAYMENTS: constant(uint256) = 200          # Max size of batchTransfer payment batches.
EST_GAS_PER_TRANSFER: constant(uint256) = 6000 # Initial estimate of the cost for a single payment transfer.


# ERC20 State Variables
totalSupply: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])


# Events
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256

event OwnershipTransfer:
    previousOwner: indexed(address)
    newOwner: indexed(address)

event GasRemaining:
    gas_remaining: indexed(uint256)

event BatchTransfer:
    sender: indexed(address)
    tx_count: uint256
    tx_value: uint256   
    gas_per_tx: uint256 
    gas_exhausted : bool


owner: public(address)
isMinter: public(HashMap[address, bool])


@external
def __init__():
    self.owner = msg.sender
    self.totalSupply = 0


@pure
@external
def name() -> String[20]:
    return NAME


@pure
@external
def symbol() -> String[5]:
    return SYMBOL


@pure
@external
def decimals() -> uint8:
    return DECIMALS


@external
def transfer(receiver: address, amount: uint256) -> bool:
    # Display msg.gas here to see what we start with.
    log GasRemaining(msg.gas)

    assert receiver != ZERO_ADDRESS, "Cannot transfer to null address."
    self.balanceOf[msg.sender] -= amount
    self.balanceOf[receiver] += amount

    log Transfer(msg.sender, receiver, amount)

    # Display msg.gas here to see what we end with.
    log GasRemaining(msg.gas)

    return True


struct Payment:
    receiver: address
    amount: uint256
    

@external
def batchTransfer(payments: DynArray[Payment, MAX_PAYMENTS], min_gas_remaining: uint256 = MIN_GAS_REMAINING) -> uint256:
    pay_count: uint256 = 0
    pay_value: uint256 = 0
    per_transfer_cost: uint256 = EST_GAS_PER_TRANSFER
    gas_remaining : uint256 = msg.gas
    gas_exhausted: bool = False

    log GasRemaining(msg.gas)

    for payment in payments:

        # Break if we don't have sufficient gas.
        if msg.gas < (min_gas_remaining + per_transfer_cost): 
            gas_exhausted = True
            break

        # We're complete if any receiver is a zero address.
        if payment.receiver == ZERO_ADDRESS: break

        self.balanceOf[msg.sender] -= payment.amount
        self.balanceOf[payment.receiver] += payment.amount

        log GasRemaining(msg.gas)

        log Transfer(msg.sender, payment.receiver, payment.amount)

        pay_count += 1
        pay_value += payment.amount

        if per_transfer_cost == EST_GAS_PER_TRANSFER:
            per_transfer_cost = gas_remaining - msg.gas
        if per_transfer_cost < gas_remaining - msg.gas:
            per_transfer_cost = gas_remaining - msg.gas
        gas_remaining = msg.gas
    
    # Log the batch event here.
    log BatchTransfer(msg.sender, pay_count, pay_value, per_transfer_cost, gas_exhausted)

    log GasRemaining(msg.gas)

    return pay_count


@external
def transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    """
    @notice
        Similar to transfer, but used for allowing contracts to send tokens on your
        behalf. For example a decentralized exchange would make use of this method,
        once given authorization via the approve method.
    """
    assert receiver != ZERO_ADDRESS, "Cannot transfer to null address."
    self.allowance[sender][msg.sender] -= amount
    self.balanceOf[sender] -= amount
    self.balanceOf[receiver] += amount

    log Transfer(sender, receiver, amount)
    return True


@external
def approve(spender: address, amount: uint256) -> bool:
    """
    @param spender The address that will execute on owner behalf.
    @param amount The amount of token to be transfered.
    """
    self.allowance[msg.sender][spender] = amount

    log Approval(msg.sender, spender, amount)
    return True


@external
def burn(amount: uint256) -> bool:
    """
    @notice Burns the supplied amount of tokens from the sender wallet.
    @param amount The amount of token to be burned.
    @return A boolean that indicates if the operation was successful.
    """
    assert self.balanceOf[msg.sender] >= amount, "Burn amount exceeds balance."

    self.balanceOf[msg.sender] -= amount
    self.totalSupply -= amount

    log Transfer(msg.sender, ZERO_ADDRESS, amount)
    return True


@external
def mint(receiver: address, amount: uint256) -> bool:
    """
    @notice Function to mint new tokens.
    @param receiver The address that will receive the minted tokens.
    @param amount The amount of tokens to mint.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner or self.isMinter[msg.sender], "Access denied."

    self.totalSupply += amount
    self.balanceOf[receiver] += amount

    log Transfer(ZERO_ADDRESS, receiver, amount)
    return True


@external
def addMinter(target: address) -> bool:
    """
    @notice Function to grant minter role to targeted address.
    @param target Address to have token minter role granted.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner
    assert target != ZERO_ADDRESS, "Cannot add null address as minter."
    self.isMinter[target] = True
    return True


@external
def removeMinter(target: address) -> bool:
    """
    @notice Function to remove minter role to targeted address.
    @param target Address to have token minter role removed.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner, "Access denied."
    assert self.isMinter[target] == True, "Targeted address is not a minter."
    self.isMinter[target] = False
    return True


@external
def transferOwnership(target: address) -> bool:
    """
    @notice Function to transfer ownership from one address to another.
    @param target Address of the new owner.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner, "Access denied."
    assert target != ZERO_ADDRESS, "Cannot add null address as owner."

    # revoke owner's minting role as well
    self.isMinter[self.owner] = False
    self.owner = target

    log OwnershipTransfer(msg.sender, target)
    return True
