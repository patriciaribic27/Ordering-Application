"""
Demo za Strategy pattern - demonstrira dinamičku promjenu strategije cijene.
"""

from models.beverage import Coffee, Tea, Beer
from models.factory import BeverageFactory
from services.pricing_strategy import StandardPricingStrategy, HappyHourStrategy, BulkDiscountStrategy


def main():
    print("=== Strategy Pattern Demo ===\n")
    
    # Kreiraj pića
    coffee = BeverageFactory.create("Coffee")
    tea = BeverageFactory.create("Tea")
    beer = BeverageFactory.create("Beer")
    
    # Standardne cijene
    print("STANDARDNE CIJENE:")
    print(f"Coffee: {coffee.price():.2f} EUR (osnovna: {coffee.base_price():.2f} EUR)")
    print(f"Tea: {tea.price():.2f} EUR (osnovna: {tea.base_price():.2f} EUR)")
    print(f"Beer: {beer.price():.2f} EUR (osnovna: {beer.base_price():.2f} EUR)")
    print()
    
    # Happy Hour - 20% popusta
    print("HAPPY HOUR (20% popust):")
    happy_hour = HappyHourStrategy(discount_percentage=20.0)
    
    coffee.set_pricing_strategy(happy_hour)
    tea.set_pricing_strategy(happy_hour)
    beer.set_pricing_strategy(happy_hour)
    
    print(f"Coffee: {coffee.price():.2f} EUR (ušteda: {coffee.base_price() - coffee.price():.2f} EUR)")
    print(f"Tea: {tea.price():.2f} EUR (ušteda: {tea.base_price() - tea.price():.2f} EUR)")
    print(f"Beer: {beer.price():.2f} EUR (ušteda: {beer.base_price() - beer.price():.2f} EUR)")
    print()
    
    # Ekstremni popust - 50%
    print("SPECIJALNA AKCIJA (50% popust):")
    mega_discount = HappyHourStrategy(discount_percentage=50.0)
    
    coffee.set_pricing_strategy(mega_discount)
    print(f"Coffee: {coffee.price():.2f} EUR (pola cijene!)")
    print()
    
    # Vraćanje na standardnu cijenu
    print("VRAĆANJE NA STANDARDNE CIJENE:")
    standard = StandardPricingStrategy()
    coffee.set_pricing_strategy(standard)
    tea.set_pricing_strategy(standard)
    beer.set_pricing_strategy(standard)
    
    print(f"Coffee: {coffee.price():.2f} EUR")
    print(f"Tea: {tea.price():.2f} EUR")
    print(f"Beer: {beer.price():.2f} EUR")
    print()
    
    # Demonstracija da različita pića mogu imati različite strategije istovremeno
    print("MJEŠOVITO - različite strategije za različita pića:")
    coffee.set_pricing_strategy(StandardPricingStrategy())
    tea.set_pricing_strategy(HappyHourStrategy(15.0))
    beer.set_pricing_strategy(HappyHourStrategy(30.0))
    
    print(f"Coffee: {coffee.price():.2f} EUR (standardna cijena)")
    print(f"Tea: {tea.price():.2f} EUR (15% popust)")
    print(f"Beer: {beer.price():.2f} EUR (30% popust)")


if __name__ == "__main__":
    main()
