import random
import string
import time
import logging
import threading
import requests
import shutil
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("miner.log"), logging.StreamHandler()],
)

CONFIG = {
    "API_URL": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
    "MINING_DELAY": 0.1,
    "PROBABILITY": 0.000001,  # 0,0001% de chance de encontrar Bitcoin
    "BLOCKS_PER_ROUND": 10,  # 10 blocos por rodada
    "BLOCK_VALUE": 10,  # Cada bloco vale 10
}

class MiningError(Exception):
    pass

class APIError(MiningError):
    pass

TITLE = """
 /$$$$$$$  /$$$$$$ /$$$$$$$$ /$$$$$$   /$$$$$$  /$$$$$$ /$$   /$$
| $$__  $$|_  $$_/|__  $$__//$$__  $$ /$$__  $$|_  $$_/| $$$ | $$
| $$  \ $$  | $$     | $$  | $$  \__/| $$  \ $$  | $$  | $$$$| $$
| $$$$$$$   | $$     | $$  | $$      | $$  | $$  | $$  | $$ $$ $$
| $$__  $$  | $$     | $$  | $$      | $$  | $$  | $$  | $$  $$$$
| $$  \ $$  | $$     | $$  | $$    $$| $$  | $$  | $$  | $$\  $$$
| $$$$$$$/ /$$$$$$   | $$  |  $$$$$$/|  $$$$$$/ /$$$$$$| $$ \  $$
|_______/ |______/   |__/   \______/  \______/ |______/|__/  \__/
                                                                 
                                                                 
"""

def center_text(text):
    terminal_width = shutil.get_terminal_size().columns
    return "\n".join(" " * ((terminal_width - len(line)) // 2) + line for line in text.splitlines())

def generate_fake_address():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(34))

def fetch_bitcoin_price():
    try:
        response = requests.get(CONFIG["API_URL"], timeout=5)
        response.raise_for_status()
        return response.json()["bitcoin"]["usd"]
    except Exception as e:
        logging.error(f"Error fetching Bitcoin price: {e}")
        raise APIError("Failed to fetch Bitcoin price.")

def mine_block():
    address = generate_fake_address()
    if random.random() < CONFIG["PROBABILITY"]:
        bitcoin_price = fetch_bitcoin_price()
        if bitcoin_price:
            return address, bitcoin_price * CONFIG["BLOCK_VALUE"]  # Multiplica pelo valor do bloco
    return address, None

def mining_round(round_number):
    print(center_text(Fore.YELLOW + f"=== Round {round_number} ==="))
    results = []
    with tqdm(total=CONFIG["BLOCKS_PER_ROUND"], desc="Mining", unit="block") as progress_bar:
        for _ in range(CONFIG["BLOCKS_PER_ROUND"]):
            try:
                address, bitcoin_value = mine_block()
                if bitcoin_value:
                    results.append((address, bitcoin_value))
                progress_bar.update(1)
                time.sleep(CONFIG["MINING_DELAY"])
            except Exception as e:
                logging.error(f"Error during mining: {e}")
                break

    total_bitcoins = len(results)
    total_value = sum(value for _, value in results)
    print(center_text(Fore.GREEN + f"Round {round_number} complete! Found {total_bitcoins} BTC (Total Value: ${total_value:.2f})"))
    return total_bitcoins, total_value

def simulate_mining():
    print(center_text(Fore.YELLOW + TITLE))
    print(center_text(Fore.YELLOW + "Starting ultra-rare Bitcoin mining simulation..."))
    print(center_text(Fore.YELLOW + "Press Ctrl + C to stop."))
    
    round_number = 1
    total_bitcoins_all_rounds = 0
    total_value_all_rounds = 0.0

    try:
        while True:
            bitcoins, value = mining_round(round_number)
            total_bitcoins_all_rounds += bitcoins
            total_value_all_rounds += value
            print(center_text(Fore.CYAN + f"Total after {round_number} rounds: {total_bitcoins_all_rounds} BTC (${total_value_all_rounds:.2f})"))
            round_number += 1
    except KeyboardInterrupt:
        print(center_text(Fore.YELLOW + "\nMining stopped by the user. Goodbye!"))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(center_text(Fore.RED + f"An error occurred: {e}"))

if __name__ == "__main__":
    simulate_mining()
