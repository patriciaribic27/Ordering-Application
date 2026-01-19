from abc import ABC, abstractmethod


class PricingStrategy(ABC):
    """Abstract base class for pricing strategies."""
    
    @abstractmethod
    def calculate_price(self, base_price: float) -> float:
        """
        Calculates the final price based on the base price.
        
        Args:
            base_price: Base price of the beverage
            
        Returns:
            Final price after applying the strategy
        """
        pass


class StandardPricingStrategy(PricingStrategy):
    """Standard strategy - returns base price without modifications."""
    
    def calculate_price(self, base_price: float) -> float:
        return base_price


class HappyHourStrategy(PricingStrategy):
    """Happy Hour strategy - applies discount to price."""
    
    def __init__(self, discount_percentage: float = 20.0):
        """
        Initialize Happy Hour strategy with discount.
        
        Args:
            discount_percentage: Discount percentage (default 20%)
        """
        self.discount_percentage = discount_percentage
    
    def calculate_price(self, base_price: float) -> float:
        discount = base_price * (self.discount_percentage / 100)
        return base_price - discount


class BulkDiscountStrategy(PricingStrategy):
    """Strategy for discount on bulk quantities."""
    
    def __init__(self, min_quantity: int = 5, discount_percentage: float = 10.0):
        """
        Initialize strategy with discount for larger quantity.
        
        Args:
            min_quantity: Minimum quantity for discount
            discount_percentage: Discount percentage
        """
        self.min_quantity = min_quantity
        self.discount_percentage = discount_percentage
    
    def calculate_price(self, base_price: float, quantity: int = 1) -> float:
        if quantity >= self.min_quantity:
            discount = base_price * (self.discount_percentage / 100)
            return base_price - discount
        return base_price
