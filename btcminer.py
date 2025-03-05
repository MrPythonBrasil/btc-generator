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
    "INITIAL_PROBABILITY": 0.0001,
    "PROBABILITY_INCREMENT": 0.00001,
    "MAX_PROBABILITY": 0.01,
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

def mine_block(probability):
    address = generate_fake_address()
    if random.random() < probability:
        bitcoin_price = fetch_bitcoin_price()
        if bitcoin_price:
            return address, bitcoin_price
    return address, None

def mining_thread(progress_bar, results):
    probability = CONFIG["INITIAL_PROBABILITY"]
    while not progress_bar.n >= progress_bar.total:
        address, bitcoin_price = mine_block(probability)
        if bitcoin_price:
            results.append((address, bitcoin_price))
            probability = min(probability + CONFIG["PROBABILITY_INCREMENT"], CONFIG["MAX_PROBABILITY"])
        progress_bar.update(1)
        time.sleep(CONFIG["MINING_DELAY"])

def simulate_mining():
    print(center_text(Fore.YELLOW + TITLE))
    print(center_text(Fore.YELLOW + "Starting advanced Bitcoin mining simulation..."))
    print(center_text(Fore.YELLOW + "Press Ctrl + C to stop."))
    
    results = []
    total_blocks = 1000
    num_threads = 4

    with tqdm(total=total_blocks, desc="Mining", unit="block") as progress_bar:
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=mining_thread, args=(progress_bar, results))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    total_bitcoins = len(results)
    total_value = sum(price for _, price in results)
    print(center_text(Fore.GREEN + f"Mining complete! Found {total_bitcoins} BTC (Total Value: ${total_value:.2f})"))

if __name__ == "__main__":
    try:
        simulate_mining()
    except KeyboardInterrupt:
        print(center_text(Fore.YELLOW + "\nMining stopped by the user. Goodbye!"))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(center_text(Fore.RED + f"An error occurred: {e}"))
