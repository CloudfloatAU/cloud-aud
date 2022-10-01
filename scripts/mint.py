"""
Script to mint new tokens. Only the creator of the contract or an account with minter
role can mint new tokens!

Make sure that an account with minting role is in your current ape environment.
Docs: https://docs.apeworx.io/ape/stable/userguides/accounts.html#live-network-accounts
"""

from pprint import pprint

from ape import project
from ape.cli import get_user_selected_account


account = get_user_selected_account()
token = project.Token


def mint(contract_address: str, amount: int):
    contract = token.at(contract_address)
    contract.mint(account, amount * int(1e8), sender=account)


def main():
    amount, contract_address = "", ""

    # Get amount of tokens to be minted. This can be an integer only, for simplicity.
    while not amount.isdigit():
        amount = input("⛏ How many tokens would you like to mint? ")

    # Determine token contract address. An account can deploy multiple contracts, we
    # want to select the appropriate one.
    pprint(token.deployments)
    while len(contract_address) != 42:
        contract_address = input("🗃 What is the contract address? ")

    mint(contract_address=contract_address, amount=int(amount))
