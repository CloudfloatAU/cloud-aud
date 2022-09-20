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

owner: public(address)
isMinter: public(HashMap[address, bool])
isBurner: public(HashMap[address, bool])


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
    assert receiver != ZERO_ADDRESS, "Cannot transfer to null address"
    self.balanceOf[msg.sender] -= amount
    self.balanceOf[receiver] += amount

    log Transfer(msg.sender, receiver, amount)
    return True


@external
def transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    """
    @notice
        Similar to transfer, but used for allowing contracts to send tokens on your
        behalf. For example a decentralized exchange would make use of this method,
        once given authorization via the approve method.
    """
    assert receiver != ZERO_ADDRESS, "Cannot transfer to null address"
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
    @notice Function to burn tokens from total supply by deducting sender's address balance
    @param amount The amount of tokens to be burned.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner or self.isBurner[msg.sender], "Access is denied."
    assert self.balanceOf[msg.sender] >= amount, "Burn amount exceeds targeted balance."

    self.totalSupply -= amount
    self.balanceOf[msg.sender] -= amount

    log Transfer(msg.sender, ZERO_ADDRESS, amount)
    return True


@external
def burnFrom(target: address, amount: uint256) -> bool:
    """
    @notice Function to burn tokens from total supply by deducting target's address balance
    @param target The address that will have its balance deducted.
    @param amount The amount of tokens to be burned.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner or self.isBurner[msg.sender], "Access is denied."
    assert target != ZERO_ADDRESS, "Cannot burn from null address."
    assert self.balanceOf[target] >= amount, "Burn amount exceeds targeted balance."

    self.totalSupply -= amount
    self.balanceOf[target] -= amount

    log Transfer(target, ZERO_ADDRESS, amount)
    return True


@external
def mint(receiver: address, amount: uint256) -> bool:
    """
    @notice Function to mint new tokens.
    @param receiver The address that will receive the minted tokens.
    @param amount The amount of tokens to mint.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner or self.isMinter[msg.sender], "Access is denied."

    self.totalSupply += amount
    self.balanceOf[receiver] += amount

    log Transfer(ZERO_ADDRESS, receiver, amount)
    return True


@external
def addBurner(target: address) -> bool:
    """
    @notice Function to grant burner role to targeted address.
    @param target  Address to have token burner role granted.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner, "Access is denied."
    assert target != ZERO_ADDRESS, "Cannot add null address as burner"
    self.isBurner[target] = True
    return True


@external
def removeBurner(target: address) -> bool:
    """
    @notice Function to remove burner role to targeted address.
    @param target Address to have token burner role removed.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner, "Access is denied."
    assert self.isBurner[target] == True, "Targeted address is not a burner"
    self.isBurner[target] = False
    return True


@external
def revokeBurner() -> bool:
    """
    @notice Function to revoke own burner role from sender.
    @return A boolean that indicates if the operation was successful.
    """
    assert self.isBurner[msg.sender] == True, "Sender is not a burner"
    self.isBurner[msg.sender] = False
    return True


@external
def addMinter(target: address) -> bool:
    """
    @notice Function to grant minter role to targeted address.
    @param target Address to have token minter role granted.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner
    assert target != ZERO_ADDRESS, "Cannot add null address as minter"
    self.isMinter[target] = True
    return True


@external
def removeMinter(target: address) -> bool:
    """
    @notice Function to remove minter role to targeted address.
    @param target Address to have token minter role removed.
    @return A boolean that indicates if the operation was successful.
    """
    assert msg.sender == self.owner
    assert self.isMinter[target] == True, "Targeted address is not a minter"
    self.isMinter[target] = False
    return True
