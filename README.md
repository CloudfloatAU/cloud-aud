# Cloud AUD

Cloud AUD (**CAUD**) is an interest-bearing stablecoin redeemable one to one for
Australian Dollar.

Generated from [token-template](https://github.com/ApeAcademy/token-template) by
[Ape Academy](https://academy.apeworx.io).

## Deploy the contract

This project uses vyper via the [ape](https://github.com/apeWorX/ape) framework. With
ape installed, install the required plugins with:

```shell
ape plugins install .
```

To compile and deploy the contract, [add an account via ape](https://docs.apeworx.io/ape/stable/userguides/accounts.html)
and run:

```shell
ape compile
ape run scripts/deploy.py --network ethereum:ropsten:infura
```

Make sure to replace the network with whichever network you want to use.
