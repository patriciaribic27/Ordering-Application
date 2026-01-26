"""
Kompletna demonstracija automatskog prebacivanja strategije.
Pokazuje sve scenarije: Happy Hour, Standard, i Bulk Discount.
"""

import logging
from datetime import datetime
from unittest.mock import patch
from services.pricing_strategy import PricingContext, BulkDiscountStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


def demo_scenario(hour: int, orders: list):
    """
    Demonstrira narudžbe u određeno vrijeme.
    
    Args:
        hour: Sat dana (0-23)
        orders: Lista (name, price, quantity) tuple-ova
    """
    mock_time = datetime.now().replace(hour=hour, minute=0, second=0)
    
    print(f"\n{'='*70}")
    print(f"🕐 SCENARIO: {mock_time.strftime('%H:%M')} - ", end="")
    if 16 <= hour < 18:
        print("HAPPY HOUR PERIOD 🎉")
    else:
        print("STANDARD PRICING 💼")
    print('='*70)
    
    with patch('services.pricing_strategy.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_time
        
        total = 0
        print()
        
        for name, price, quantity in orders:
            # Auto-select strategy based on time
            context = PricingContext(auto_select=True)
            
            # Override with bulk discount if needed
            if quantity >= 5:
                context.set_strategy(BulkDiscountStrategy(5, 10.0))
                print(f"🔄 Bulk order ({quantity} items) - Switching to BulkDiscountStrategy")
            
            # Calculate price
            final_price = context.calculate(price, quantity, log_calculation=False)
            original = price * quantity
            savings = original - final_price
            
            # Display order
            print(f"📦 {name}")
            print(f"   Unit price: {price:.2f}€ x {quantity} = {original:.2f}€")
            print(f"   Strategy: {context.get_strategy_name()}")
            
            if savings > 0:
                print(f"   💰 Savings: {savings:.2f}€ ({(savings/original)*100:.0f}% off)")
            
            print(f"   ✅ Final: {final_price:.2f}€")
            print()
            
            total += final_price
        
        print(f"{'─'*70}")
        print(f"💰 TOTAL: {total:.2f}€")
        print(f"{'='*70}")


def main():
    """Demonstrira različite scenarije tokom dana."""
    
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "AUTOMATIC STRATEGY SELECTION" + " "*25 + "║")
    print("║" + " "*15 + "Complete Demo of All Scenarios" + " "*22 + "║")
    print("╚" + "="*68 + "╝")
    
    # Define orders
    morning_orders = [
        ("Coffee", 3.5, 1),
        ("Cappuccino", 4.0, 2),
        ("Latte", 4.5, 1),
    ]
    
    happy_hour_orders = [
        ("Beer", 5.0, 2),
        ("Wine", 6.0, 1),
        ("Cocktail", 8.0, 3),
    ]
    
    bulk_orders = [
        ("Water", 1.5, 10),  # Bulk discount
        ("Coffee", 3.5, 6),   # Bulk discount
    ]
    
    evening_orders = [
        ("Espresso", 2.5, 2),
        ("Tea", 2.0, 1),
    ]
    
    # Run scenarios
    demo_scenario(10, morning_orders)      # Morning - Standard pricing
    demo_scenario(16, happy_hour_orders)   # Happy Hour - 20% discount
    demo_scenario(17, bulk_orders)         # Happy Hour + Bulk override
    demo_scenario(20, evening_orders)      # Evening - Standard pricing
    
    # Summary
    print("\n\n" + "╔" + "="*68 + "╗")
    print("║" + " "*26 + "SUMMARY" + " "*35 + "║")
    print("╚" + "="*68 + "╝\n")
    
    print("📊 AUTOMATIC BEHAVIOR:")
    print("-" * 70)
    print("  10:00 → StandardPricingStrategy")
    print("         (Normal pricing)")
    print()
    print("  16:00 → HappyHourStrategy (20% discount)")
    print("         (Automatically activated!)")
    print()
    print("  17:00 → HappyHourStrategy + Bulk Override")
    print("         (Bulk discount priority for ≥5 items)")
    print()
    print("  20:00 → StandardPricingStrategy")
    print("         (Happy Hour ended)")
    print()
    print("─" * 70)
    print()
    print("✨ Strategy changes AUTOMATICALLY based on time!")
    print("✨ No user input required!")
    print("✨ All logic is centralized in PricingContext!")
    print()
    print("🎯 Strategy Pattern properly implemented! 🎉")
    print()


if __name__ == "__main__":
    main()
