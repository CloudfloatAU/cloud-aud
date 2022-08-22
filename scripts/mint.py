from ape import project
from ape.cli import get_user_selected_account


def mint(token_deployment_id: int, amount: float):
    account = get_user_selected_account()
    token = project.Token
    contract = token.deployments[token_deployment_id]
    contract.mint(account, amount * 100000000, sender=account)


def main():
    mint(token_deployment_id=3, amount=100)
