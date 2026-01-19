from abc import ABC, abstractmethod
from models.factory import BeverageRegistryMeta
from services.pricing_strategy import PricingStrategy, StandardPricingStrategy


class Beverage(ABC, metaclass=BeverageRegistryMeta):
    """Abstract base class for beverages."""
    
    def __init__(self):
        self._pricing_strategy: PricingStrategy = StandardPricingStrategy()
    
    @abstractmethod
    def base_price(self) -> float:
        """Returns the base price of the beverage."""
        pass
    
    def price(self) -> float:
        """Returns the beverage price using the current strategy."""
        return self._pricing_strategy.calculate_price(self.base_price())
    
    def set_pricing_strategy(self, strategy: PricingStrategy):
        """Sets a new pricing strategy."""
        self._pricing_strategy = strategy
    
    def get_pricing_strategy(self) -> PricingStrategy:
        """Returns the current pricing strategy."""
        return self._pricing_strategy


class Coffee(Beverage):
    """Coffee - basic implementation."""
    
    def base_price(self) -> float:
        return 2.50


class Tea(Beverage):
    """Tea - basic implementation."""
    
    def base_price(self) -> float:
        return 2.00


class Beer(Beverage):
    """Beer - basic implementation."""
    
    def base_price(self) -> float:
        return 3.50


class Cappuccino(Beverage):
    """Cappuccino - coffee with milk."""
    
    def base_price(self) -> float:
        return 3.00


class Espresso(Beverage):
    """Espresso - quick coffee."""
    
    def base_price(self) -> float:
        return 2.00


class Latte(Beverage):
    """Latte - coffee with lots of milk."""
    
    def base_price(self) -> float:
        return 3.50


class Water(Beverage):
    """Water - simple beverage."""
    
    def base_price(self) -> float:
        return 1.00


class Juice(Beverage):
    """Juice - fruit beverage."""
    
    def base_price(self) -> float:
        return 2.80


class CocaCola(Beverage):
    """Coca Cola - carbonated soft drink."""
    
    def base_price(self) -> float:
        return 2.50


class Wine(Beverage):
    """Wine - alcoholic beverage."""
    
    def base_price(self) -> float:
        return 4.50
