"""
Script to deploy the Cloud AUD token (contracts/Token.vy) from a selected wallet to a
specified network.

See README.md instructions to run this script.
"""

from ape import project
from ape.cli import get_user_selected_account


def main():
    account = get_user_selected_account()
    account.deploy(project.Token)
