"""
Quick test to demonstrate that all decorators are now in use.
Run this to see decorators in action and check log.txt.
"""

import sys
from pathlib import Path

# Add parent directory to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from models.factory import BeverageFactory
from services.order_service import OrderService
from services.menu_service import MenuService


def test_decorators():
    """Test that all decorators are working."""
    print("=" * 70)
    print("TESTING ALL DECORATORS")
    print("=" * 70)
    
    log_file = Path(__file__).parent / "log.txt"
    
    # Clear old log
    if log_file.exists():
        log_file.unlink()
    
    print("\n1. Testing Factory with performance_log + log_calls")
    print("-" * 70)
    
    # This will trigger performance_log and log_calls decorators
    beverage1 = BeverageFactory.create("Coffee")
    print(f"   Created: {beverage1.__class__.__name__}")
    
    beverage2 = BeverageFactory.create("Espresso")
    print(f"   Created: {beverage2.__class__.__name__}")
    
    print("\n2. Testing async decorators in OrderService")
    print("-" * 70)
    
    async def test_order_service():
        service = OrderService()
        
        # This will trigger log_async_calls and catch_async_exceptions
        order = await service.create_order("Coffee", 1, 2.5, 0.1)
        print(f"   Created order: {order.id}")
        
        # Wait a bit
        await asyncio.sleep(0.2)
        
        # Cancel order (also uses decorators)
        result = await service.cancel_order(order.id)
        print(f"   Cancelled: {result}")
    
    asyncio.run(test_order_service())
    
    print("\n3. Testing async decorators in MenuService")
    print("-" * 70)
    
    async def test_menu_service():
        service = MenuService("http://localhost:8080")
        
        # This will trigger log_async_calls, performance_log_async, catch_async_exceptions
        # Will fail since server is not running, but that's OK for testing decorators
        result = await service.fetch_menu()
        print(f"   Menu fetch result: {result}")
    
    asyncio.run(test_menu_service())
    
    print("\n" + "=" * 70)
    print("✅ ALL DECORATORS TESTED")
    print("=" * 70)
    
    # Check log file
    if log_file.exists():
        print(f"\n📄 Log file created: {log_file}")
        print(f"   Size: {log_file.stat().st_size} bytes")
        print(f"\n   Preview of log entries:")
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10], 1):
                print(f"   {i}. {line.strip()}")
            if len(lines) > 10:
                print(f"   ... and {len(lines) - 10} more entries")
    else:
        print("❌ Log file not found!")


if __name__ == "__main__":
    test_decorators()
