"""
Primjer korištenja BeverageFactory s automatskom registracijom.

Ovaj skript demonstrira kako factory automatski registrira sve
klase pića bez potrebe za ručnim dodavanjem.
"""

from models.beverage import Coffee, Tea, Beer
from models.factory import BeverageFactory


def main():
    print("=== BeverageFactory Demo ===\n")
    
    # Prikaz dostupnih pića
    print("Dostupna pića:")
    for beverage in BeverageFactory.get_available_beverages():
        print(f"  - {beverage}")
    print()
    
    # Kreiranje pića kroz factory
    print("Kreiranje pića:")
    
    coffee = BeverageFactory.create("Coffee")
    print(f"Coffee cijena: {coffee.price()} EUR")
    
    tea = BeverageFactory.create("Tea")
    print(f"Tea cijena: {tea.price()} EUR")
    
    beer = BeverageFactory.create("Beer")
    print(f"Beer cijena: {beer.price()} EUR")
    
    # Testiranje s malim slovima
    print("\nKreiranje s malim slovima:")
    coffee2 = BeverageFactory.create("coffee")
    print(f"coffee cijena: {coffee2.price()} EUR")
    
    # Testiranje nepoznatog pića
    print("\nTestiranje nepoznatog pića:")
    try:
        unknown = BeverageFactory.create("Juice")
    except ValueError as e:
        print(f"Greška: {e}")


if __name__ == "__main__":
    main()
