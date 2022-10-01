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
