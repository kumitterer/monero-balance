import subprocess
import time
import os
from flask import Flask, jsonify, Response
from prometheus_client import Gauge, generate_latest
from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPCWallet

app = Flask(__name__)

wallet_path = os.environ.get("MONERO_WALLET_PATH", "wallet/readonly")
rpc_host = os.environ.get("MONERO_RPC_HOST", "localhost")
rpc_port = os.environ.get("MONERO_RPC_PORT", 18083)
daemon_address = os.environ.get(
    "MONERO_DAEMON_ADDRESS", "xmr-node.cakewallet.com:18081"
)
wallet_password = os.environ.get("MONERO_WALLET_PASSWORD", "")

listen_port = os.environ.get("PORT", 5000)
listen_host = os.environ.get("HOST", "localhost")

skip_wallet_rpc = os.environ.get("MONERO_SKIP_RPC", False)

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# Function to start the Monero wallet RPC server
def start_rpc_server():
    rpc_command = [
        "monero-wallet-rpc",
        "--wallet-file",
        wallet_path,
        "--rpc-bind-port",
        str(rpc_port),
        "--daemon-address",
        daemon_address,
        "--password",
        wallet_password,
        "--disable-rpc-login",
    ]
    return subprocess.Popen(rpc_command)


# Function to check if the RPC server is up
def is_rpc_server_up(host, port):
    try:
        wallet = Wallet(JSONRPCWallet(host=host, port=port))
        wallet.height()  # Try to get the current blockchain height, just to check if the RPC server is up
        return True
    except ConnectionError:
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if not skip_wallet_rpc:
    # Start the wallet RPC server using the public node
    wallet_rpc_process = start_rpc_server()

    # Wait for the wallet RPC server to be up
    while not is_rpc_server_up("localhost", rpc_port):
        log("Waiting for the wallet RPC server to start...")
        time.sleep(2)

    log("Wallet RPC server is up!")

# Connect to the Monero wallet RPC server
wallet = Wallet(JSONRPCWallet(host=rpc_host, port=rpc_port))

# Prometheus gauge for the balance
balance_gauge = Gauge("monero_wallet_balance", "Current balance of the Monero wallet")


@app.route("/balance")
def get_balance():
    balance = wallet.balance()
    balance_gauge.set(balance)
    return jsonify({"balance": balance})


@app.route("/metrics")
def metrics():
    balance = wallet.balance()
    balance_gauge.set(balance)
    return Response(generate_latest(), mimetype="text/plain")


if __name__ == "__main__":
    try:
        app.run(host=listen_host, port=listen_port)
    finally:
        # Ensure the RPC server is terminated when the application exits
        wallet_rpc_process.terminate()
