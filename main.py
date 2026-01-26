"""
Main entry point for the cafe ordering tablet application.

This is the primary way to launch the application.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main() -> None:
    """Start the cafe ordering application."""
    print("=" * 60)
    print("🍹 CAFE ORDERING TABLET APPLICATION")
    print("=" * 60)
    print("\nStarting GUI...")
    print("Note: REST API will start automatically on http://localhost:8080")
    print()
    
    # Import and start GUI
    try:
        from gui.tablet_gui import main as gui_main
        gui_main()
    except KeyboardInterrupt:
        print("\n\n👋 Application closed by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

