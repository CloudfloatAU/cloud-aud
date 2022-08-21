from ape import project
from ape.cli import get_user_selected_account


def main():
    account = get_user_selected_account()
    token = project.Token
    contract = token.deployments[0]
    contract.mint(account, 123, sender=account)
