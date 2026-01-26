"""
Test script that simulates different times to verify strategy switching.
This uses monkey patching to test Happy Hour behavior at any time.
"""

import logging
from datetime import datetime, time
from unittest.mock import patch
from services.pricing_strategy import (
    PricingContext,
    StandardPricingStrategy,
    HappyHourStrategy
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


def test_strategy_at_time(hour: int, minute: int = 0):
    """
    Test strategy selection at a specific time.
    
    Args:
        hour: Hour to test (0-23)
        minute: Minute to test (0-59)
    """
    # Create a mock datetime for the specified time
    mock_now = datetime.now().replace(hour=hour, minute=minute, second=0)
    
    print(f"\n{'='*70}")
    print(f"🕐 Testing at time: {mock_now.strftime('%H:%M:%S')}")
    print(f"{'='*70}")
    
    # Patch datetime.now() to return our mock time
    with patch('services.pricing_strategy.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_now
        
        # Create context with auto_select
        context = PricingContext(auto_select=True)
        
        # Test price calculation
        base_price = 10.0
        quantity = 2
        
        print(f"\n📊 Order: {quantity}x item @ {base_price}€ each")
        final_price = context.calculate(base_price, quantity)
        
        print(f"✅ Strategy used: {context.get_strategy_name()}")
        print(f"💰 Final price: {final_price:.2f}€")
        
        # Check expected behavior
        if 16 <= hour < 18:
            expected_price = base_price * quantity * 0.8  # 20% discount
            expected_strategy = "HappyHourStrategy"
            print(f"🎉 HAPPY HOUR ACTIVE - Expected 20% discount")
        else:
            expected_price = base_price * quantity
            expected_strategy = "StandardPricingStrategy"
            print(f"💼 Standard pricing - No discount")
        
        # Verify
        if context.get_strategy_name() == expected_strategy:
            print(f"✅ Correct strategy applied")
        else:
            print(f"❌ Wrong strategy! Expected {expected_strategy}")
        
        if abs(final_price - expected_price) < 0.01:
            print(f"✅ Correct price calculated")
        else:
            print(f"❌ Wrong price! Expected {expected_price:.2f}€")


def main():
    """Run tests for various times throughout the day."""
    print("=" * 70)
    print("🧪 TESTING AUTOMATIC STRATEGY SWITCHING AT DIFFERENT TIMES")
    print("=" * 70)
    
    # Test various times throughout the day
    test_times = [
        (9, 0, "Morning - Before Happy Hour"),
        (12, 30, "Lunch time - Before Happy Hour"),
        (15, 30, "Afternoon - Just before Happy Hour"),
        (16, 0, "Happy Hour START - 16:00"),
        (16, 30, "Happy Hour MIDDLE - 16:30"),
        (17, 45, "Happy Hour END - 17:45"),
        (18, 0, "After Happy Hour - 18:00"),
        (20, 0, "Evening - After Happy Hour"),
        (23, 0, "Late night - After Happy Hour"),
    ]
    
    for hour, minute, description in test_times:
        print(f"\n\n{'#'*70}")
        print(f"# {description}")
        print(f"{'#'*70}")
        test_strategy_at_time(hour, minute)
    
    print("\n\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 70)
    print()
    print("📊 SUMMARY:")
    print("  - StandardPricingStrategy: Used OUTSIDE of 16:00-18:00")
    print("  - HappyHourStrategy (20% off): Used BETWEEN 16:00-18:00")
    print()
    print("🎯 The strategy switches AUTOMATICALLY based on time!")
    print("   No manual intervention or GUI checkboxes required.")
    print()


if __name__ == "__main__":
    main()
