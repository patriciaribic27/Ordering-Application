"""
Test script for demonstrating parallel order processing with multiple GUI instances.
This script launches multiple tablet GUIs to simulate multiple tables ordering simultaneously.
"""

import subprocess
import sys
import time
from pathlib import Path

def main():
    """Launch multiple GUI instances for parallel order testing."""
    
    gui_script = Path(__file__).parent / "gui" / "tablet_gui.py"
    
    print("=" * 70)
    print("🚀 PARALLEL ORDER PROCESSING TEST")
    print("=" * 70)
    print("\nThis will launch multiple tablet GUIs to demonstrate:")
    print("  ✓ Asynchronous menu fetching from REST API")
    print("  ✓ Parallel processing of multiple orders")
    print("  ✓ Multiple tables ordering simultaneously")
    print("\n" + "=" * 70)
    
    # Ask how many instances
    try:
        num_instances = int(input("\nHow many tablet instances to launch? (1-5): ").strip() or "2")
        num_instances = max(1, min(5, num_instances))
    except ValueError:
        num_instances = 2
    
    print(f"\n📱 Launching {num_instances} tablet GUI instance(s)...\n")
    
    processes = []
    
    for i in range(num_instances):
        print(f"  Starting Tablet #{i+1}...")
        
        # Launch GUI in separate process
        proc = subprocess.Popen(
            [sys.executable, str(gui_script)],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        processes.append(proc)
        
        # Small delay between launches
        time.sleep(0.5)
    
    print(f"\n✅ {num_instances} tablet(s) launched successfully!")
    print("\n" + "=" * 70)
    print("📊 WHAT TO OBSERVE:")
    print("=" * 70)
    print("\n1. REST API SERVER:")
    print("   - First GUI starts the server on http://localhost:8080")
    print("   - Other GUIs connect to the same server")
    print("   - Check console for 'REST API server started' message")
    
    print("\n2. MENU FETCHING:")
    print("   - Each GUI fetches menu from API asynchronously")
    print("   - Status bar shows 'Fetching menu from REST API...'")
    print("   - Then shows '✅ Menu loaded from API: X beverages available'")
    
    print("\n3. PARALLEL ORDER PROCESSING:")
    print("   - Create orders in different GUIs simultaneously")
    print("   - Each order is processed asynchronously")
    print("   - Status bar shows 'Processing N order(s) in parallel'")
    print("   - Orders don't block each other or the GUI")
    
    print("\n4. PRICE FETCHING:")
    print("   - Prices are fetched from REST API (not hardcoded)")
    print("   - Console shows '💰 Price from API: ...'")
    print("   - If API unavailable, falls back to Factory pattern")
    
    print("\n" + "=" * 70)
    print("\n💡 TIP: Look at the status bar at the bottom of each GUI")
    print("    It shows real-time info about API connection and active orders")
    
    print("\n⏸️  Press Ctrl+C to close all tablets and exit...\n")
    
    try:
        # Wait for user to close
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Closing all tablets...")
        for proc in processes:
            proc.terminate()
        print("✅ All tablets closed.\n")

if __name__ == "__main__":
    main()
