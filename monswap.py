import json
import time
from web3 import Web3
import pyfiglet
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Create ASCII banner
banner = pyfiglet.figlet_format("Si GUNDUL")
print(Fore.MAGENTA + Style.BRIGHT + banner)
print(Fore.CYAN + Style.BRIGHT + "Auto Swap MON to WMON and Auto Withdraw")
print(Fore.CYAN + Style.BRIGHT + "BOT Created By https://t.me/sigundulmania")



RPC_URL = 'https://testnet-rpc.monad.xyz/'
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Cek koneksi ke node Monad
if not web3.is_connected():
    print(Fore.RED + "❌ Gagal terhubung ke Monad Testnet RPC! Periksa koneksi Anda.")
    exit()

# Ambil chain ID dari node
CHAIN_ID = web3.eth.chain_id
print(Fore.GREEN + f"✅ Terhubung ke Monad Testnet! Chain ID: {CHAIN_ID}")

WMON = Web3.to_checksum_address("0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701")

def send_transaction_with_retry(transaction, private_key, max_retries=10, delay=10):
    retries = 0
    while retries < max_retries:
        try:
            nonce = web3.eth.get_transaction_count(transaction['from'], 'pending')
            transaction['nonce'] = nonce
            transaction['gas'] = web3.eth.estimate_gas(transaction)  # Estimasi gas sebelum transaksi
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(Fore.GREEN + f"✅ Transaksi berhasil! TX Hash: {tx_hash.hex()}")
            return tx_hash
        except Exception as e:
            if 'nonce too low' in str(e):
                print(Fore.YELLOW + "⚠️ Nonce terlalu rendah, mencoba lagi...")
                time.sleep(5)
                continue
            print(Fore.MAGENTA + f"⚠️ Gagal mengirim transaksi: {e}. Mencoba ulang dalam {delay} detik...")
            time.sleep(delay)
            retries += 1
    print(Fore.RED + "❌ Gagal mengirim transaksi setelah beberapa kali percobaan.")
    return None

def deposit_mon_to_wmon(wallet, amount_in_mon, gas_price):
    try:
        amount_in_wei = web3.to_wei(amount_in_mon, 'ether')
        deposit_function_selector = web3.keccak(text="deposit()")[:4]

        txn = {
            'from': Web3.to_checksum_address(wallet.address),
            'to': WMON,
            'value': amount_in_wei,
            'gasPrice': web3.to_wei(gas_price, 'gwei'),
            'nonce': web3.eth.get_transaction_count(wallet.address, 'pending'),
            'chainId': CHAIN_ID,
            'data': deposit_function_selector.hex()
        }
        
        send_transaction_with_retry(txn, wallet.key)
        print(Fore.GREEN + f"✅ [{wallet.address}] Berhasil deposit MON ke WMON")
        time.sleep(5)
        withdraw_wmon_to_mon(wallet, amount_in_wei, gas_price)  # Auto withdraw setelah deposit
    except Exception as error:
        print(Fore.MAGENTA + f"\n❌ [{wallet.address}] Gagal deposit MON ke WMON: {error}")

def withdraw_wmon_to_mon(wallet, amount_in_wei, gas_price):
    try:
        amount_in_wei = int(amount_in_wei)  # Pastikan amount_in_wei bertipe int
        withdraw_function_selector = web3.keccak(text="withdraw(uint256)")[:4]
        amount_padded = amount_in_wei.to_bytes(32, 'big')
        data = withdraw_function_selector + amount_padded
        
        txn = {
            'from': Web3.to_checksum_address(wallet.address),
            'to': WMON,
            'gasPrice': web3.to_wei(gas_price, 'gwei'),
            'nonce': web3.eth.get_transaction_count(wallet.address, 'pending'),
            'chainId': CHAIN_ID,
            'data': data.hex()
        }
        
        send_transaction_with_retry(txn, wallet.key)
        print(Fore.GREEN + f"✅ [{wallet.address}] Berhasil withdraw WMON ke MON sebanyak {amount_in_wei} Wei")
        time.sleep(5)  # Tambahkan delay agar transaksi bisa diproses dengan baik
    except Exception as error:
        print(Fore.MAGENTA + f"\n❌ [{wallet.address}] Gagal withdraw WMON ke MON: {error}")

def process_wallets(wallets, amount, transactions_per_wallet, gas_price):
    for wallet in wallets:
        print(f"\n🚀 Memulai transaksi untuk wallet: {wallet.address}")
        for i in range(transactions_per_wallet):
            print(f"\n🔄 Transaksi {i + 1} dari {transactions_per_wallet} untuk {wallet.address}")
            deposit_mon_to_wmon(wallet, amount, gas_price)

def load_wallets():
    with open("pvkeys.txt", "r") as file:
        private_keys = [line.strip() for line in file.readlines() if line.strip()]
    return [web3.eth.account.from_key(pk) for pk in private_keys]

if __name__ == "__main__":
    amount = float(input("\n💱 Masukkan jumlah MON yang ingin di-deposit ke WMON: "))
    if amount <= 0:
        print(Fore.RED + "\n⚠️ Masukkan jumlah yang valid!")
        exit()
    transactions = int(input("\n🔁 Masukkan jumlah transaksi per wallet: "))
    if transactions <= 0:
        print(Fore.RED + "\n⚠️ Masukkan jumlah transaksi yang valid!")
        exit()
    gas_price = float(input("\n⛽ Masukkan gas price (Gwei): "))
    if gas_price <= 0:
        print(Fore.RED + "\n⚠️ Masukkan gas price yang valid!")
        exit()
    wallets = load_wallets()
    if not wallets:
        print(Fore.RED + "\n❌ Tidak ada wallet ditemukan di pvkeys.txt!")
        exit()
    print(f"\n📋 Memulai deposit dan withdraw...")
    process_wallets(wallets, amount, transactions, gas_price)
    print(Fore.GREEN + "\n🎉 Semua transaksi selesai!")
