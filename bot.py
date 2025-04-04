import random
import requests
from web3 import Web3
from colorama import Fore, Style, init
import time
import os
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()

# Tea-Sepolia Testnet Configuration (default values)
CHAIN_ID = 10218
CURRENCY_SYMBOL = "TEA"  # Untuk token native
DECIMALS = 18  # Set to the token's decimals (commonly 18 for most tokens)

# ABI for the ERC-20 token contract (Standard ERC-20 ABI for transfers)
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
    }
]

def print_header():
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 50)
    print(Fore.MAGENTA + Style.BRIGHT + "Auto Send TEA Tokens".center(50))
    print(Fore.YELLOW + "Telegram: @airdrop_node".center(50))
    print(Fore.CYAN + "Bot created by: https://t.me/airdrop_node".center(50))
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 50)

# Transfer Native TEA tokens function
def transfer_native_token(sender, senderkey, recipient, amount, web3, retries=3):
    for attempt in range(retries):
        try:
            token_amount = web3.to_wei(amount, 'ether')  # Convert TEA to wei (native unit)
            nonce = web3.eth.get_transaction_count(sender)
            base_gas_price = web3.eth.gas_price
            gas_price = int(base_gas_price * (1.2 + attempt * 0.1))

            transaction = {
                'chainId': CHAIN_ID,
                'from': sender,
                'to': recipient,
                'value': token_amount,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
            }

            signed_txn = web3.eth.account.sign_transaction(transaction, senderkey)
            print(Fore.CYAN + f'Memproses pengiriman {amount} {CURRENCY_SYMBOL} (native) ke alamat: {recipient} ...')

            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            txid = web3.to_hex(tx_hash)
            web3.eth.wait_for_transaction_receipt(tx_hash)

            print(Fore.GREEN + f'Pengiriman {amount} {CURRENCY_SYMBOL} (native) ke {recipient} berhasil!')
            print(Fore.GREEN + f'TX-ID : {txid}')
            print(Fore.CYAN + f'Block Explorer: https://sepolia.tea.xyz/tx/{txid}')
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

# Transfer ERC-20 tokens function
def transfer_erc20_token(sender, senderkey, recipient, amount, web3, token_address, token_name, retries=3):
    for attempt in range(retries):
        try:
            token_contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
            token_amount = int(amount * (10 ** DECIMALS))
            nonce = web3.eth.get_transaction_count(sender)
            base_gas_price = web3.eth.gas_price
            gas_price = int(base_gas_price * (1.2 + attempt * 0.1))

            txn = token_contract.functions.transfer(recipient, token_amount).build_transaction({
                'chainId': CHAIN_ID,
                'from': sender,
                'gas': 200000,
                'gasPrice': gas_price,
                'nonce': nonce,
            })

            signed_txn = web3.eth.account.sign_transaction(txn, senderkey)
            print(Fore.CYAN + f'Memproses pengiriman {amount} {token_name} (ERC-20) ke alamat: {recipient} ...')

            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            txid = web3.to_hex(tx_hash)
            web3.eth.wait_for_transaction_receipt(tx_hash)

            print(Fore.GREEN + f'Pengiriman {amount} {token_name} (ERC-20) ke {recipient} berhasil!')
            print(Fore.GREEN + f'TX-ID : {txid}')
            print(Fore.CYAN + f'Block Explorer: https://sepolia.tea.xyz/tx/{txid}')
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

# Fetch recipient addresses from URL
def fetch_recipient_addresses(web3, url="https://raw.githubusercontent.com/choir94/Send/refs/heads/main/Kyc-address.txt"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        lines = response.text.strip().split('\n')
        addresses = []
        for addr in lines:
            addr = addr.strip()
            if web3.is_address(addr):
                addresses.append(web3.to_checksum_address(addr))
            else:
                print(Fore.RED + f"Alamat tidak valid dari URL: {addr}")
        if not addresses:
            print(Fore.RED + "Tidak ada alamat valid yang ditemukan di URL!")
            return None
        print(Fore.GREEN + f"Berhasil memuat {len(addresses)} alamat dari URL.")
        return addresses
    except requests.RequestException as e:
        print(Fore.RED + f"Gagal mengunduh daftar alamat dari URL: {e}")
        return None

# Check if the RPC URL is valid, retry if not
def check_rpc_url(rpc_url, retries=3):
    for attempt in range(retries):
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if web3.is_connected():
                print(Fore.GREEN + "Terhubung ke RPC dengan sukses!")
                chain_id = web3.eth.chain_id
                print(Fore.CYAN + f"Chain ID: {chain_id}")
                if chain_id != CHAIN_ID:
                    print(Fore.RED + f"Chain ID ({chain_id}) tidak sesuai dengan Tea-Sepolia ({CHAIN_ID})!")
                    return None
                return web3
            else:
                print(Fore.RED + "Gagal terhubung ke RPC. Periksa URL dan coba lagi.")
        except Exception as e:
            print(Fore.RED + f"Error menghubungkan ke RPC pada percobaan {attempt + 1}: {e}")
        if attempt < retries - 1:
            print(Fore.YELLOW + f"Mencoba ulang dalam 5 detik... ({attempt + 1}/{retries})")
            time.sleep(5)
        else:
            print(Fore.RED + f"Gagal terhubung ke RPC setelah {retries} percobaan.")
    return None

# Main execution
print_header()

# Load RPC URL from .env or use default
default_rpc = "https://tea-sepolia.g.alchemy.com/public"
RPC_URL = os.getenv("RPC_URL", default_rpc)
print(Fore.YELLOW + f"Menggunakan RPC URL: {RPC_URL}")

# Check and connect to the provided RPC URL
web3 = check_rpc_url(RPC_URL)
if not web3:
    exit()

# Load private key from .env
private_key = os.getenv("PRIVATE_KEY")
if not private_key:
    print(Fore.RED + "Private key tidak ditemukan di file .env! Tambahkan PRIVATE_KEY ke .env.")
    exit()
try:
    sender = web3.eth.account.from_key(private_key)
    print(Fore.GREEN + f"Wallet pengirim: {sender.address}")
except ValueError as e:
    print(Fore.RED + f"Private key tidak valid: {e}")
    exit()

# Ask the user for the type of token to send
print(Fore.YELLOW + "Pilih jenis token yang akan dikirim:")
print(Fore.YELLOW + "1. Native TEA")
print(Fore.YELLOW + "2. ERC-20 Token")
token_type = input("Masukkan pilihan (1 atau 2): ").strip()

# Variabel untuk menyimpan nama token ERC-20
token_name = None
if token_type == "2":
    TOKEN_ADDRESS = input("Masukkan alamat kontrak ERC-20 token: ").strip()
    token_name = input("Masukkan nama token ERC-20 (contoh: USDT, DAI): ").strip()

# Fetch recipient addresses from the URL
recipient_addresses = fetch_recipient_addresses(web3)
if not recipient_addresses:
    exit()

# Ask the user how many transactions to process
loop = int(input(f"Berapa banyak transaksi yang ingin diproses? (max {len(recipient_addresses)}): "))
if loop > len(recipient_addresses):
    print(Fore.RED + f"Jumlah transaksi melebihi jumlah alamat yang tersedia ({len(recipient_addresses)}). Menyesuaikan ke {len(recipient_addresses)}.")
    loop = len(recipient_addresses)

# Ask the user how much to send per transaction
prompt_symbol = CURRENCY_SYMBOL if token_type == "1" else token_name
amount = float(input(f"Berapa banyak {prompt_symbol} yang akan dikirim per transaksi (contoh: 0.001)?: "))

# Make a copy of the address list to avoid modifying the original
available_addresses = recipient_addresses.copy()

for i in range(loop):
    print(Fore.CYAN + f"\nMemproses Transaksi {i + 1}/{loop}")
    
    # Pilih alamat secara acak dari daftar yang tersedia
    recipient_addr = random.choice(available_addresses)
    
    # Transfer tokens based on user choice
    if token_type == "1":
        transfer_native_token(sender.address, private_key, recipient_addr, amount, web3)
    elif token_type == "2":
        transfer_erc20_token(sender.address, private_key, recipient_addr, amount, web3, TOKEN_ADDRESS, token_name)
    else:
        print(Fore.RED + "Pilihan token tidak valid. Hanya masukkan 1 atau 2.")
        break

    # Add random delay between 20 and 60 seconds (except for the last transaction)
    if i < loop - 1:
        delay = random.uniform(20, 60)
        print(Fore.YELLOW + f"Menunggu {delay:.2f} detik sebelum transaksi berikutnya...")
        time.sleep(delay)

print(Fore.GREEN + "\nSemua transaksi selesai.")
