# Monero Balance Exporter

This is a simple Prometheus exporter for Monero wallets. It uses the `monero-wallet-rpc` to get the balance of a wallet and exports it as a Prometheus metric.

## Usage

```bash
MONERO_WALLET_PATH=/path/to/your/wallet MONERO_WALLET_PASSWORD="YourWalletPassword!" python balance.py
```

This will start the exporter on port 5000. You can change the port by setting the `PORT` environment variable.

The script handles starting a `monero-wallet-rpc` process and connecting to it, so ensure that the `MONERO_RPC_PORT` is set if the default of `18083` is already in use, or set `MONERO_SKIP_RPC` to any value to skip starting the `monero-wallet-rpc` process and connect to an existing one.

## Metrics

The exporter only exposes one metric:

- `monero_wallet_balance` - The balance of the wallet in XMR.

The metrics are exposed on the `/metrics` endpoint.

## JSON

The exporter also exposes the balance as a JSON object on the `/balance` endpoint.
