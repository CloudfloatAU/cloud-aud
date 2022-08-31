from ape import project
from ape.cli import get_user_selected_account


def mint(token_deployment_id: int, amount: int):
    account = get_user_selected_account()
    token = project.Token
    contract = token.deployments[token_deployment_id]
    contract.mint(account, amount * 100000000, sender=account)


def main():
    amount, token_deployment_id = "", ""
    while not amount.isdigit():
        amount = input("How many tokens would you like to mint? ")
    while not token_deployment_id.isdigit():
        token_deployment_id = input("What is the token deployment index? ")
    mint(token_deployment_id=int(token_deployment_id), amount=int(amount))
