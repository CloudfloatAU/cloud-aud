<div align="center">
  <img src="https://github.com/CloudfloatAU/cloud-aud/raw/main/cloudfloat.png" style="height: 50px; width: 50px; border-radius: 10px; margin-top: 20px;">
  <h1>Cloud AUD</h1>
  <p>Cloud AUD (<b>CAUD</b>) is an interest-bearing stablecoin redeemable one to one for Australian Dollar.</p>
  <p>Generated from <a href="https://github.com/ApeAcademy/token-template">token-template</a> by <a href="https://academy.apeworx.io">Ape Academy</a>.</p>
</div>

<div align="center">
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  <a href="https://github.com/CloudfloatAU/cloud-aud/actions/workflows/lint.yml"><img src="https://github.com/CloudfloatAU/cloud-aud/actions/workflows/lint.yml/badge.svg"></a>
  <a href="https://github.com/CloudfloatAU/cloud-aud/actions/workflows/test.yaml"><img src="https://github.com/CloudfloatAU/cloud-aud/actions/workflows/test.yaml/badge.svg"></a>
  <a href="https://github.com/CloudfloatAU/cloud-aud/actions/workflows/docs.yml"><img src="https://github.com/CloudfloatAU/cloud-aud/actions/workflows/docs.yml/badge.svg"></a>
</div>


## Usage

This project uses [Vyper](https://vyper.readthedocs.io/en/stable/) via the
[ape](https://github.com/apeWorX/ape) framework. Install the requirements and required
plugins with:

```shell
pip install -r requirements.txt
ape plugins install .
```

You will also most likely need an account (a.k.a. wallet) to perform any on-chain
action.  
[Add an account via ape](https://docs.apeworx.io/ape/stable/userguides/accounts.html).


### Deploy the contract

To compile and deploy the contract, run:

```shell
ape compile
ape run scripts/deploy.py --network ethereum:ropsten:geth
```

*A funded account is required to deploy the contract.*


### Mint new tokens

**⚠️ Only the creator of the contract or an account with minter role can mint new
tokens!**

```shell
ape compile
ape run scripts/mint.py --network ethereum:ropsten:geth
```


## Contribute

### Coding style

This project uses [black](https://github.com/psf/black) code formatter, which is an
extension of [PEP8](https://peps.python.org/pep-0008/).

<details>
<summary>More info on how to use black.</summary>

```shell
# To automatically format your code, do the following:
# install black if you haven't already
pip install black

# format every Python file in the current working directory
black .

# or format a single file
black file.py
```
</details>
