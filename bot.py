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

# ABI for the ERC-20 token contract (Standard ERC-20 ABI for transfers)
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {
                "name": "to",
                "type": "address"
            },
            {
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def print_header():
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 50)
    print(Fore.MAGENTA + Style.BRIGHT + "Auto Send TEA Tokens".center(50))
    print(Fore.YELLOW + "Telegram: @airdrop_node".center(50))
    print(Fore.CYAN + "Bot created by: https://t.me/airdrop_node".center(50))
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 50)

# Transfer ERC-20 tokens function
def TransferToken(sender, senderkey, recipient, amount, web3, retries=3):
    for attempt in range(retries):
        try:
            # Prepare the contract
            token_contract = web3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)

            # Convert the amount to the token's smallest unit (e.g., Wei for ETH, but here it's token's decimals)
            token_amount = web3.to_wei(amount, 'ether')  # Adjust based on the token's decimal precision

            # Build the transaction details manually
            transaction = {
                'chainId': CHAIN_ID,
                'from': sender,
                'gas': 200000,  # You can adjust the gas limit as needed
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(sender),
                'to': TOKEN_ADDRESS,
                'data': token_contract.encodeABI(fn_name='transfer', args=[recipient, token_amount]),
            }

            # Sign the transaction
            signed_txn = web3.eth.account.sign_transaction(transaction, senderkey)
            print(Fore.CYAN + f'Processing Send {amount} Tokens To Random New Address : {recipient} ...')

            # Send the transaction
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Get transaction hash
            txid = web3.to_hex(tx_hash)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            print(Fore.GREEN + f'Send {amount} Tokens To Random New Address : {recipient} Success!')
            print(Fore.GREEN + f'TX-ID : {txid}')

            break
        except Exception as e:
            print(Fore.RED + f"Error on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print(Fore.YELLOW + f"Retrying in 5 seconds... ({attempt + 1}/{retries})")
                time.sleep(5)
            else:
                print(Fore.RED + f"Transaction failed after {retries} attempts.")

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
                print(Fore.GREEN + "Connected to RPC successfully!")
                chain_id = web3.eth.chain_id  # Try to get the chain ID
                print(Fore.CYAN + f"Chain ID: {chain_id}")
                return web3
            else:
                print(Fore.RED + "Failed to connect to RPC. Please check the URL and try again.")
                if attempt < retries - 1:
                    print(Fore.YELLOW + f"Retrying in 5 seconds... ({attempt + 1}/{retries})")
                    time.sleep(5)
        except Exception as e:
            print(Fore.RED + f"Error connecting to RPC on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print(Fore.YELLOW + f"Retrying in 5 seconds... ({attempt + 1}/{retries})")
                time.sleep(5)
        if attempt == retries - 1:
            print(Fore.RED + f"Failed to connect to RPC after {retries} attempts.")
            return None

# Main execution
print_header()

# Ask the user for the token address
TOKEN_ADDRESS = input("Please enter the ERC-20 Token contract address: ").strip()

# Use Tea-Assam Testnet RPC URL
web3 = check_rpc_url(RPC_URL)

# Ask the user for their private key
private_key = input("Please enter your private key : ")
sender = web3.eth.account.from_key(private_key)

# Ask the user how many transactions to process
loop = int(input("How many transactions do you want to process? : "))

# Ask the user how much to send per transaction
amount = float(input("How much TEA Tokens to send per transaction (e.g., 0.001)?: "))

for i in range(loop):
    print(Fore.CYAN + f"\nProcessing Transaction {i + 1}/{loop}")

    # Generate a new random recipient address for each transaction
    recipient = generate_random_recipient(web3)

    # Transfer ERC-20 tokens using sender's address and private key
    TransferToken(sender.address, private_key, recipient.address, amount, web3)

print(Fore.GREEN + "\nAll transactions completed.")

