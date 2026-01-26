"""
Test script for time-based automatic strategy selection.
This demonstrates that the strategy changes automatically based on time.
"""

import logging
from datetime import datetime
from services.pricing_strategy import (
    PricingContext,
    StandardPricingStrategy,
    HappyHourStrategy
)

# Configure logging to see strategy selection
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


def test_automatic_strategy():
    """Test automatic strategy selection based on current time."""
    print("=" * 70)
    print("🕐 TIME-BASED STRATEGY PATTERN TEST")
    print("=" * 70)
    print()
    
    current_time = datetime.now()
    current_hour = current_time.hour
    
    print(f"Current time: {current_time.strftime('%H:%M:%S')}")
    print(f"Current hour: {current_hour}")
    print()
    
    # Test 1: Automatic strategy selection
    print("📋 Test 1: Creating PricingContext with auto_select=True")
    print("-" * 70)
    context = PricingContext(auto_select=True)
    print()
    
    # Test pricing calculation
    base_price = 5.0
    quantity = 2
    
    print(f"📊 Calculating price for {quantity}x Coffee @ {base_price}€")
    final_price = context.calculate(base_price, quantity)
    print(f"✅ Final price: {final_price:.2f}€")
    print(f"🎯 Active strategy: {context.get_strategy_name()}")
    print()
    
    # Expected behavior
    print("=" * 70)
    print("📌 EXPECTED BEHAVIOR:")
    print("-" * 70)
    if 16 <= current_hour < 18:
        print("✅ Current time is between 16:00 and 18:00")
        print("✅ Happy Hour is ACTIVE")
        print("✅ HappyHourStrategy should be used (20% discount)")
        print(f"✅ Expected price: {base_price * quantity * 0.8:.2f}€")
        expected_strategy = "HappyHourStrategy"
    else:
        print("ℹ️  Current time is NOT between 16:00 and 18:00")
        print("ℹ️  Standard pricing is active")
        print("ℹ️  StandardPricingStrategy should be used (no discount)")
        print(f"ℹ️  Expected price: {base_price * quantity:.2f}€")
        expected_strategy = "StandardPricingStrategy"
    
    print()
    
    # Verify result
    actual_strategy = context.get_strategy_name()
    if actual_strategy == expected_strategy:
        print(f"✅ SUCCESS: Strategy matches expected ({expected_strategy})")
    else:
        print(f"❌ ERROR: Strategy mismatch!")
        print(f"   Expected: {expected_strategy}")
        print(f"   Actual: {actual_strategy}")
    
    print()
    print("=" * 70)
    
    # Test 2: Manual strategy update
    print()
    print("📋 Test 2: Manual strategy refresh with update_strategy_by_time()")
    print("-" * 70)
    context.update_strategy_by_time()
    print(f"🎯 Strategy after update: {context.get_strategy_name()}")
    print()
    
    # Test 3: Multiple orders
    print("📋 Test 3: Processing multiple orders")
    print("-" * 70)
    orders = [
        ("Espresso", 3.5, 1),
        ("Latte", 4.5, 2),
        ("Cappuccino", 4.0, 3),
    ]
    
    total = 0
    for name, price, qty in orders:
        order_price = context.calculate(price, qty)
        total += order_price
        print()
    
    print(f"\n💰 Total for all orders: {total:.2f}€")
    print()
    print("=" * 70)


if __name__ == "__main__":
    test_automatic_strategy()
    
    print()
    print("💡 TIP: To test Happy Hour behavior:")
    print("   - Run this script between 16:00 and 18:00 to see HappyHourStrategy")
    print("   - Run at other times to see StandardPricingStrategy")
    print()
    print("🔧 To manually test different times, you can temporarily modify")
    print("   the time check in pricing_strategy.py _select_strategy_by_time()")
    print()
