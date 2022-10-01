# Use a hardware wallet

## Trezor

You will need the [`ape-trezor`](https://github.com/ApeWorX/ape-trezor) plugin. Install
it with the following command:

```shell
ape plugins install trezor
```

Then, add the Trezor account to `ape`:

```shell
ape trezor add --hd-path "m/44'/1'/0'/0" trezor

# you will be prompted to unlock your Trezor, and to select which account you want to
# import
```

`--hd-path "m/44'/1'/0'/0"` indicates Trezor's default derivation path. You will not be
able to sign transactions using a different derivation path by default ([learn more](https://github.com/trezor/trezor-firmware/issues/1336#issuecomment-720126545)).

Your Trezor account is now ready, you can now interact with the contract as you normally
would.


## Ledger

You will need the [`ape-ledger`](https://github.com/ApeWorX/ape-ledger) plugin. Install
it with the following command:

```shell
ape plugins install ledger
```

You must:

- have the Ledger USB device connected
- have the Ledger USB device unlocked (by entering the passcode)
- and have the Ethereum app open, then run:

```shell
ape ledger add ledger
```

**⚠️ You need to enable [blind signing](https://support.ledger.com/hc/en-us/articles/4499092909085-Allowing-blind-signing-in-the-Solana-SOL-app?docs=true)
to interact with the contract:**

![](https://support.ledger.com/hc/article_attachments/4499097590173/solana_blind.gif)

**⚠️ Currently, the ape-ledger plugin only supports Ethereum.** [See related issue](https://github.com/ApeWorX/ape-ledger/issues/23).

Your Ledger account is now ready, you can now interact with the contract as you normally
would.
