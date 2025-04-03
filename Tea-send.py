import random
import secrets
from web3 import Web3
from colorama import Fore, Style, init
import time

# Initialize colorama
init(autoreset=True)

# Tea-Sepolia Testnet Configuration
RPC_URL = "https://tea-sepolia.g.alchemy.com/public"
CHAIN_ID = 10218
CURRENCY_SYMBOL = "TEA"
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

            # Mengambil nonce terbaru untuk pengirim
            nonce = web3.eth.get_transaction_count(sender)

            # Meningkatkan gas price agar lebih tinggi dari transaksi sebelumnya
            base_gas_price = web3.eth.gas_price
            gas_price = int(base_gas_price * (1.2 + attempt * 0.1))  # Tambahkan 20% setiap percobaan

            transaction = {
                'chainId': CHAIN_ID,
                'from': sender,
                'to': recipient,
                'value': token_amount,
                'gas': 21000,  # Gas limit untuk transfer native token
                'gasPrice': gas_price,
                'nonce': nonce,
            }

            signed_txn = web3.eth.account.sign_transaction(transaction, senderkey)
            print(Fore.CYAN + f'Memproses pengiriman {amount} {CURRENCY_SYMBOL} (native) ke alamat: {recipient} ...')

            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
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
def transfer_erc20_token(sender, senderkey, recipient, amount, web3, token_address, retries=3):
    for attempt in range(retries):
        try:
            token_contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
            token_amount = int(amount * (10 ** DECIMALS))

            # Mengambil nonce terbaru untuk pengirim
            nonce = web3.eth.get_transaction_count(sender)

            # Meningkatkan gas price agar lebih tinggi dari transaksi sebelumnya
            base_gas_price = web3.eth.gas_price
            gas_price = int(base_gas_price * (1.2 + attempt * 0.1))  # Tambahkan 20% setiap percobaan

            transaction = {
                'chainId': CHAIN_ID,
                'from': sender,
                'gas': 200000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'to': token_address,
                'data': token_contract.encodeABI(fn_name='transfer', args=[recipient, token_amount]),
            }

            signed_txn = web3.eth.account.sign_transaction(transaction, senderkey)
            print(Fore.CYAN + f'Memproses pengiriman {amount} token ERC-20 ke alamat: {recipient} ...')

            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            txid = web3.to_hex(tx_hash)
            web3.eth.wait_for_transaction_receipt(tx_hash)

            print(Fore.GREEN + f'Pengiriman {amount} token ERC-20 ke {recipient} berhasil!')
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

# Generate a random recipient address
def generate_random_recipient(web3):
    priv = secrets.token_hex(32)  # Generate a new private key
    private_key = "0x" + priv
    recipient = web3.eth.account.from_key(private_key)
    print(Fore.YELLOW + f"Alamat acak yang di-generate: {recipient.address}")
    return recipient

# Load recipient addresses from manual input
def load_manual_recipient_addresses(web3):
    print(Fore.YELLOW + "Paste daftar alamat di bawah ini (satu alamat per baris), tekan Enter dua kali untuk selesai:")
    lines = []
    while True:
        line = input()
        if line == "":  # Enter dua kali (baris kosong) untuk mengakhiri input
            if not lines:  # Jika belum ada input, lanjutkan meminta
                print(Fore.RED + "Masukkan setidaknya satu alamat!")
                continue
            break
        lines.append(line.strip())
    
    addresses = []
    for addr in lines:
        if web3.is_address(addr):
            addresses.append(web3.to_checksum_address(addr))
        else:
            print(Fore.RED + f"Alamat tidak valid: {addr}")
    if not addresses:
        print(Fore.RED + "Tidak ada alamat valid yang dimasukkan!")
        return None
    print(Fore.GREEN + f"Berhasil memuat {len(addresses)} alamat dari input manual.")
    return addresses

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

# Use Tea-Sepolia Testnet RPC URL
web3 = check_rpc_url(RPC_URL)
if not web3:
    exit()

# Ask the user for their private key
private_key = input("Masukkan private key Anda: ")
sender = web3.eth.account.from_key(private_key)

# Ask the user for the type of token to send
print(Fore.YELLOW + "Pilih jenis token yang akan dikirim:")
print(Fore.YELLOW + "1. Native TEA")
print(Fore.YELLOW + "2. ERC-20 Token")
token_type = input("Masukkan pilihan (1 atau 2): ").strip()

if token_type == "2":
    # Ask for the ERC-20 token address
    TOKEN_ADDRESS = input("Masukkan alamat kontrak ERC-20 token: ").strip()

# Ask the user for the recipient type
print(Fore.YELLOW + "Pilih jenis penerima:")
print(Fore.YELLOW + "1. Generate alamat acak")
print(Fore.YELLOW + "2. Input manual banyak alamat (max 1000)")
recipient_type = input("Masukkan pilihan (1 atau 2): ").strip()

recipient_addresses = None
if recipient_type == "2":
    recipient_addresses = load_manual_recipient_addresses(web3)
    if not recipient_addresses:
        exit()

# Ask the user how many transactions to process
loop = int(input("Berapa banyak transaksi yang ingin diproses? (max 1000 untuk alamat manual): "))
if recipient_type == "2" and loop > len(recipient_addresses):
    print(Fore.RED + f"Jumlah transaksi melebihi jumlah alamat yang dimasukkan ({len(recipient_addresses)}). Menyesuaikan ke {len(recipient_addresses)}.")
    loop = len(recipient_addresses)
if loop > 1000:
    print(Fore.YELLOW + "Jumlah transaksi dibatasi maksimum 1000.")
    loop = 1000

# Ask the user how much to send per transaction
amount = float(input(f"Berapa banyak {CURRENCY_SYMBOL} yang akan dikirim per transaksi (contoh: 0.001)?: "))

for i in range(loop):
    print(Fore.CYAN + f"\nMemproses Transaksi {i + 1}/{loop}")

    # Determine recipient based on user choice
    if recipient_type == "1":
        recipient = generate_random_recipient(web3)
        recipient_addr = recipient.address
    elif recipient_type == "2":
        recipient_addr = recipient_addresses[i % len(recipient_addresses)]  # Cycle through addresses if loop > len(addresses)
    else:
        print(Fore.RED + "Pilihan penerima tidak valid. Hanya masukkan 1 atau 2.")
        break

    # Transfer tokens based on user choice
    if token_type == "1":
        transfer_native_token(sender.address, private_key, recipient_addr, amount, web3)
    elif token_type == "2":
        transfer_erc20_token(sender.address, private_key, recipient_addr, amount, web3, TOKEN_ADDRESS)
    else:
        print(Fore.RED + "Pilihan token tidak valid. Hanya masukkan 1 atau 2.")
        break

print(Fore.GREEN + "\nSemua transaksi selesai.")
