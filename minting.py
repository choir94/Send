import random
import secrets
from web3 import Web3
from colorama import Fore, Style, init
import time

# Initialize colorama
init(autoreset=True)

# Tea-Assam Testnet Configuration
RPC_URL = "https://assam-rpc.tea.xyz"
CHAIN_ID = 93384
CURRENCY_SYMBOL = "$TEA"
DECIMALS = 18  # Set to the token's decimals (commonly 18 for most tokens)

# ABI for the ERC-20 token contract (Standard ERC-20 ABI for transfers and minting)
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    # Mint function ABI (Assuming the contract has a mint function)
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "mint",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

def print_header():
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 50)
    print(Fore.MAGENTA + Style.BRIGHT + "Mint & Send TEA Tokens".center(50))
    print(Fore.YELLOW + "Telegram: @airdrop_node".center(50))
    print(Fore.CYAN + "Bot created by: https://t.me/airdrop_node".center(50))
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 50)

# Mint function
def mint_token(sender, senderkey, recipient, amount, web3, retries=3):
    for attempt in range(retries):
        try:
            token_contract = web3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)
            token_amount = int(amount * (10 ** DECIMALS))

            # Mengambil nonce terbaru untuk pengirim
            nonce = web3.eth.get_transaction_count(sender)

            # Meningkatkan gas price agar lebih tinggi dari transaksi sebelumnya
            base_gas_price = web3.eth.gas_price
            gas_price = int(base_gas_price * (1.2 + attempt * 0.1))  # Tambahkan 20% setiap percobaan

            # Transaksi mint
            transaction = {
                'chainId': CHAIN_ID,
                'from': sender,
                'gas': 200000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'to': TOKEN_ADDRESS,
                'data': token_contract.encodeABI(fn_name='mint', args=[recipient, token_amount]),
            }

            signed_txn = web3.eth.account.sign_transaction(transaction, senderkey)
            print(Fore.CYAN + f'Memproses minting {amount} token ke alamat: {recipient} ...')

            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            txid = web3.to_hex(tx_hash)
            web3.eth.wait_for_transaction_receipt(tx_hash)

            print(Fore.GREEN + f'Minting {amount} token ke {recipient} berhasil!')
            print(Fore.GREEN + f'TX-ID : {txid}')
            break
        except Exception as e:
            print(Fore.RED + f"Error pada percobaan {attempt + 1}: {e}")
            if 'replacement transaction underpriced' in str(e):
                print(Fore.YELLOW + "Gas price terlalu rendah. Meningkatkan gas price untuk percobaan berikutnya...")
            if attempt < retries - 1:
                print(Fore.YELLOW + f"Mencoba lagi dalam 5 detik... ({attempt + 1}/{retries})")
                time.sleep(5)
            else:
                print(Fore.RED + f"Transaksi gagal setelah {retries} percobaan.")

# Generate a random recipient address
def generate_random_recipient(web3):
    priv = secrets.token_hex(32)  # Generate a new private key
    private_key = "0x" + priv
    recipient = web3.eth.account.from_key(private_key)
    return recipient

# Check if the RPC URL is valid, retry if not
def check_rpc_url(rpc_url, retries=3):
    for attempt in range(retries):
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if web3.is_connected():
                print(Fore.GREEN + "Terhubung ke RPC dengan sukses!")
                chain_id = web3.eth.chain_id  # Try to get the chain ID
                print(Fore.CYAN + f"Chain ID: {chain_id}")
                return web3
            else:
                print(Fore.RED + "Gagal terhubung ke RPC. Periksa URL dan coba lagi.")
                if attempt < retries - 1:
                    print(Fore.YELLOW + f"Mencoba ulang dalam 5 detik... ({attempt + 1}/{retries})")
                    time.sleep(5)
        except Exception as e:
            print(Fore.RED + f"Error menghubungkan ke RPC pada percobaan {attempt + 1}: {e}")
            if attempt < retries - 1:
                print(Fore.YELLOW + f"Mencoba ulang dalam 5 detik... ({attempt + 1}/{retries})")
                time.sleep(5)
        if attempt == retries - 1:
            print(Fore.RED + f"Gagal terhubung ke RPC setelah {retries} percobaan.")
            return None

# Main execution
print_header()

# Ask the user for the token address
TOKEN_ADDRESS = input("Masukkan alamat kontrak ERC-20 token: ").strip()

# Use Tea-Assam Testnet RPC URL
web3 = check_rpc_url(RPC_URL)

# Ask the user for their private key
private_key = input("Masukkan private key Anda: ")
sender = web3.eth.account.from_key(private_key)

# Ask the user how many transactions to process
loop = int(input("Berapa banyak transaksi yang ingin diproses?: "))

# Ask the user how much to mint per transaction
amount = float(input(f"Berapa banyak {CURRENCY_SYMBOL} yang akan di-mint per transaksi (contoh: 0.001)?: "))

for i in range(loop):
    print(Fore.CYAN + f"\nMemproses Minting {i + 1}/{loop}")

    # Generate a new random recipient address for each transaction
    recipient = generate_random_recipient(web3)

    # Mint ERC-20 tokens using sender's address and private key
    mint_token(sender.address, private_key, recipient.address, amount, web3)

print(Fore.GREEN + "\nSemua minting selesai.")
