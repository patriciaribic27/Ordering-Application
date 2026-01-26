"""
Demonstracija pravilne implementacije Strategy Pattern-a.
Pokazuje fleksibilnost i laku zamjenu strategija.
"""

import logging
from datetime import datetime
from services.pricing_strategy import (
    PricingContext,
    StandardPricingStrategy,
    HappyHourStrategy,
    BulkDiscountStrategy
)

# Configure logging to see strategy selection
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def demonstrate_strategy_pattern():
    """Demonstrira pravilan Strategy Pattern."""
    
    print("=" * 60)
    print("STRATEGY PATTERN DEMONSTRATION")
    print("=" * 60)
    
    base_price = 10.0
    quantity = 6
    
    print(f"\nBase price: {base_price}€ per item")
    print(f"Quantity: {quantity} items")
    print(f"Total without discount: {base_price * quantity}€")
    print("\n" + "-" * 60)
    
    # 1. Standard Pricing
    print("\n1️⃣  STANDARD PRICING (No discount)")
    print("-" * 60)
    context = PricingContext(StandardPricingStrategy())
    price = context.calculate(base_price, quantity)
    print(f"   Strategy: {context.get_strategy_name()}")
    print(f"   Final price: {price:.2f}€")
    
    # 2. Happy Hour Strategy
    print("\n2️⃣  HAPPY HOUR STRATEGY (20% discount)")
    print("-" * 60)
    context.set_strategy(HappyHourStrategy(discount_percentage=20.0))
    price = context.calculate(base_price, quantity)
    print(f"   Strategy: {context.get_strategy_name()}")
    print(f"   Final price: {price:.2f}€")
    print(f"   Savings: {(base_price * quantity) - price:.2f}€")
    
    # 3. Bulk Discount Strategy
    print("\n3️⃣  BULK DISCOUNT STRATEGY (10% off for 5+ items)")
    print("-" * 60)
    context.set_strategy(BulkDiscountStrategy(min_quantity=5, discount_percentage=10.0))
    price = context.calculate(base_price, quantity)
    print(f"   Strategy: {context.get_strategy_name()}")
    print(f"   Final price: {price:.2f}€")
    print(f"   Savings: {(base_price * quantity) - price:.2f}€")
    
    # 4. Custom Happy Hour (50% discount)
    print("\n4️⃣  CUSTOM HAPPY HOUR (50% discount)")
    print("-" * 60)
    context.set_strategy(HappyHourStrategy(discount_percentage=50.0))
    price = context.calculate(base_price, quantity)
    print(f"   Strategy: {context.get_strategy_name()}")
    print(f"   Final price: {price:.2f}€")
    print(f"   Savings: {(base_price * quantity) - price:.2f}€")
    
    print("\n" + "=" * 60)
    print("✅ Strategy Pattern allows easy switching at runtime!")
    print("=" * 60)
    
    # Demonstrate multiple contexts working simultaneously
    print("\n\n📋 MULTIPLE CONTEXTS SIMULTANEOUSLY")
    print("=" * 60)
    
    context1 = PricingContext(StandardPricingStrategy())
    context2 = PricingContext(HappyHourStrategy(20.0))
    context3 = PricingContext(BulkDiscountStrategy(5, 15.0))
    
    print(f"Context 1 (Standard):     {context1.calculate(5.0, 3):.2f}€")
    print(f"Context 2 (Happy Hour):   {context2.calculate(5.0, 3):.2f}€")
    print(f"Context 3 (Bulk 15%):     {context3.calculate(5.0, 5):.2f}€")
    
    print("\n✨ Each context maintains its own strategy independently!")
    print("=" * 60 + "\n")


def demonstrate_automatic_strategy():
    """Demonstrira automatsku selekciju strategije na osnovu vremena."""
    
    print("\n" + "=" * 60)
    print("🕐 AUTOMATIC TIME-BASED STRATEGY SELECTION")
    print("=" * 60)
    
    current_time = datetime.now()
    current_hour = current_time.hour
    
    print(f"\n⏰ Current time: {current_time.strftime('%H:%M:%S')}")
    
    # Create context with automatic strategy selection
    print("\n🤖 Creating PricingContext with auto_select=True...")
    context = PricingContext(auto_select=True)
    
    print(f"✅ Strategy automatically selected: {context.get_strategy_name()}")
    
    # Calculate price
    base_price = 5.0
    quantity = 2
    
    print(f"\n📊 Calculating price for {quantity}x items @ {base_price}€")
    final_price = context.calculate(base_price, quantity, log_calculation=False)
    
    print(f"💰 Final price: {final_price:.2f}€")
    
    # Explain behavior
    print("\n" + "-" * 60)
    print("📌 HOW IT WORKS:")
    print("-" * 60)
    
    if 16 <= current_hour < 18:
        print("✅ Current time is between 16:00 and 18:00")
        print("✅ Happy Hour is ACTIVE automatically")
        print("✅ HappyHourStrategy applied (20% discount)")
    else:
        print("ℹ️  Current time is NOT between 16:00 and 18:00")
        print("ℹ️  StandardPricingStrategy is used (no discount)")
        print("ℹ️  Happy Hour will activate automatically at 16:00")
    
    print("\n🎯 No manual intervention required!")
    print("🎯 Strategy changes automatically based on time!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    demonstrate_strategy_pattern()
    demonstrate_automatic_strategy()
