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


def mint(token_deployment_id: int, amount: int):
    contract = token.deployments[token_deployment_id]
    contract.mint(account, amount * 100000000, sender=account)


def main():
    amount, token_deployment_id = "", ""

    # Get amount of tokens to be minted. This can be an integer only, for simplicity.
    while not amount.isdigit():
        amount = input("⛏ How many tokens would you like to mint? ")

    # Determine token deployment id. An account can deploy multiple contracts, we
    # want to select the appropriate one.
    pprint(token.deployments)
    while not token_deployment_id.isdigit():
        token_deployment_id = input("🗃 What is the token deployment index? ")

    mint(token_deployment_id=int(token_deployment_id), amount=int(amount))
