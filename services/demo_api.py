"""
Skripta za pokretanje API servera i klijenta zajedno.
"""

import asyncio
import time
from multiprocessing import Process
from services.api_server import main as server_main
from services.menu_service import demo_fetch_menu


def run_server():
    """Pokreće API server u zasebnom procesu."""
    server_main()


async def run_client_with_delay():
    """Čeka malo da se server pokrene, pa pokreće klijenta."""
    print("Waiting for server to start...")
    await asyncio.sleep(2)
    await demo_fetch_menu()


def main():
    """Pokreće server i klijent demo."""
    print("=== Starting API Demo ===\n")
    
    # Pokreni server u zasebnom procesu
    server_process = Process(target=run_server)
    server_process.start()
    
    try:
        # Pokreni klijent
        asyncio.run(run_client_with_delay())
    except KeyboardInterrupt:
        print("\nStopping demo...")
    finally:
        # Zaustavi server
        server_process.terminate()
        server_process.join()
        print("Demo finished.")


if __name__ == '__main__':
    main()
