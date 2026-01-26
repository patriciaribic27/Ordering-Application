from abc import ABC, abstractmethod
from datetime import datetime
import logging

# Configure logger for pricing strategies
logger = logging.getLogger(__name__)


class PricingContext:
    """
    Context class that uses a pricing strategy.
    This is the core of the Strategy Pattern - allows easy strategy switching.
    
    Examples:
        >>> context = PricingContext(StandardPricingStrategy())
        >>> context.calculate(10.0)
        10.0
        >>> context.set_strategy(HappyHourStrategy(20.0))
        >>> context.calculate(10.0)
        8.0
    """
    
    def __init__(self, strategy: 'PricingStrategy' = None, auto_select: bool = False):
        """
        Initialize context with a strategy.
        
        Args:
            strategy: Initial pricing strategy (defaults to StandardPricingStrategy)
            auto_select: If True, automatically selects strategy based on time (default False)
            
        Examples:
            >>> context = PricingContext()
            >>> isinstance(context._strategy, StandardPricingStrategy)
            True
            >>> custom_strategy = HappyHourStrategy(15.0)
            >>> context = PricingContext(custom_strategy)
            >>> context._strategy == custom_strategy
            True
        """
        if auto_select:
            self._strategy = self._select_strategy_by_time()
        else:
            self._strategy = strategy if strategy else StandardPricingStrategy()
    
    def set_strategy(self, strategy: 'PricingStrategy'):
        """
        Change the pricing strategy at runtime.
        This demonstrates the flexibility of Strategy Pattern.
        
        Args:
            strategy: New pricing strategy to use
            
        Examples:
            >>> context = PricingContext()
            >>> context.calculate(10.0)
            10.0
            >>> context.set_strategy(HappyHourStrategy(50.0))
            >>> context.calculate(10.0)
            5.0
        """
        self._strategy = strategy
    
    def calculate(self, base_price: float, quantity: int = 1, log_calculation: bool = True) -> float:
        """
        Calculate price using the current strategy.
        
        Args:
            base_price: Base price per item
            quantity: Number of items (default 1)
            log_calculation: If True, logs the calculation details (default True)
            
        Returns:
            Final price after applying strategy
            
        Examples:
            >>> # Standard pricing - no discount
            >>> context = PricingContext(StandardPricingStrategy())
            >>> context.calculate(5.0, 2, log_calculation=False)
            10.0
            >>> context.calculate(10.0, 1, log_calculation=False)
            10.0
            >>> 
            >>> # Happy Hour - 20% discount
            >>> context_happy = PricingContext(HappyHourStrategy(20.0))
            >>> context_happy.calculate(10.0, 1, log_calculation=False)
            8.0
            >>> context_happy.calculate(5.0, 2, log_calculation=False)
            8.0
            >>> 
            >>> # Happy Hour - 50% discount
            >>> context_half = PricingContext(HappyHourStrategy(50.0))
            >>> context_half.calculate(10.0, 2, log_calculation=False)
            10.0
            >>> 
            >>> # Bulk discount - 10% off for 5+ items
            >>> context_bulk = PricingContext(BulkDiscountStrategy(5, 10.0))
            >>> context_bulk.calculate(10.0, 5, log_calculation=False)
            45.0
            >>> context_bulk.calculate(10.0, 3, log_calculation=False)
            30.0
        """
        # For strategies that support quantity (like BulkDiscountStrategy)
        try:
            unit_price = self._strategy.calculate_price(base_price, quantity)
            final_price = unit_price * quantity
        except TypeError:
            # For strategies that don't support quantity parameter
            unit_price = self._strategy.calculate_price(base_price)
            final_price = unit_price * quantity
        
        # Log calculation details
        if log_calculation:
            original_price = base_price * quantity
            discount = original_price - final_price
            strategy_name = self.get_strategy_name()
            
            if discount > 0:
                logger.info(
                    f"💰 Price calculation: {base_price:.2f}€ x {quantity} = {original_price:.2f}€ | "
                    f"Strategy: {strategy_name} | Discount: {discount:.2f}€ | Final: {final_price:.2f}€"
                )
            else:
                logger.info(
                    f"💰 Price calculation: {base_price:.2f}€ x {quantity} = {final_price:.2f}€ | "
                    f"Strategy: {strategy_name} | No discount applied"
                )
        
        return final_price
    
    def get_strategy_name(self) -> str:
        """
        Get the name of the current strategy.
        
        Returns:
            Strategy class name
            
        Examples:
            >>> context = PricingContext(HappyHourStrategy())
            >>> context.get_strategy_name()
            'HappyHourStrategy'
        """
        return self._strategy.__class__.__name__
    
    def _select_strategy_by_time(self) -> 'PricingStrategy':
        """
        Automatically selects pricing strategy based on current time.
        Happy Hour is active between 16:00 and 18:00.
        
        Returns:
            Appropriate pricing strategy for current time
        """
        now = datetime.now()
        current_hour = now.hour
        current_time_str = now.strftime("%H:%M:%S")
        
        # Happy Hour: 16:00 - 18:00 (4 PM - 6 PM)
        if 16 <= current_hour < 18:
            strategy = HappyHourStrategy(discount_percentage=20.0)
            logger.info(f"🎉 Happy Hour ACTIVE at {current_time_str} - Using HappyHourStrategy (20% discount)")
            return strategy
        else:
            strategy = StandardPricingStrategy()
            logger.info(f"💰 Standard pricing at {current_time_str} - Using StandardPricingStrategy")
            return strategy
    
    def update_strategy_by_time(self):
        """
        Updates the current strategy based on time.
        Call this method to refresh the strategy for time-based changes.
        """
        self._strategy = self._select_strategy_by_time()


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
    """
    Standard strategy - returns base price without modifications.
    
    Examples:
        >>> strategy = StandardPricingStrategy()
        >>> strategy.calculate_price(10.0)
        10.0
        >>> strategy.calculate_price(5.5)
        5.5
    """
    
    def calculate_price(self, base_price: float) -> float:
        """
        Calculate price without any modifications.
        
        Args:
            base_price: Base price of the beverage
            
        Returns:
            Same as base price
            
        Examples:
            >>> strategy = StandardPricingStrategy()
            >>> strategy.calculate_price(2.5)
            2.5
            >>> strategy.calculate_price(10.0)
            10.0
            >>> strategy.calculate_price(3.75)
            3.75
            >>> # No discount applied, price stays the same
            >>> strategy.calculate_price(100.0)
            100.0
        """
        return base_price


class HappyHourStrategy(PricingStrategy):
    """
    Happy Hour strategy - applies discount to price.
    
    Examples:
        >>> strategy = HappyHourStrategy(discount_percentage=20.0)
        >>> strategy.calculate_price(10.0)
        8.0
        >>> strategy = HappyHourStrategy(discount_percentage=50.0)
        >>> strategy.calculate_price(10.0)
        5.0
    """
    
    def __init__(self, discount_percentage: float = 20.0):
        """
        Initialize Happy Hour strategy with discount.
        
        Args:
            discount_percentage: Discount percentage (default 20%)
            
        Examples:
            >>> strategy = HappyHourStrategy()
            >>> strategy.discount_percentage
            20.0
            >>> strategy = HappyHourStrategy(30.0)
            >>> strategy.discount_percentage
            30.0
        """
        self.discount_percentage = discount_percentage
    
    def calculate_price(self, base_price: float) -> float:
        """
        Calculate discounted price.
        
        Args:
            base_price: Base price of the beverage
            
        Returns:
            Discounted price
            
        Examples:
            >>> # 20% discount examples
            >>> strategy = HappyHourStrategy(20.0)
            >>> strategy.calculate_price(10.0)
            8.0
            >>> strategy.calculate_price(5.0)
            4.0
            >>> strategy.calculate_price(2.5)
            2.0
            >>> # 50% discount (half price)
            >>> strategy_50 = HappyHourStrategy(50.0)
            >>> strategy_50.calculate_price(10.0)
            5.0
            >>> # 10% discount
            >>> strategy_10 = HappyHourStrategy(10.0)
            >>> strategy_10.calculate_price(10.0)
            9.0
        """
        discount = base_price * (self.discount_percentage / 100)
        return base_price - discount


class BulkDiscountStrategy(PricingStrategy):
    """
    Strategy for discount on bulk quantities.
    
    Examples:
        >>> strategy = BulkDiscountStrategy(min_quantity=5, discount_percentage=10.0)
        >>> strategy.calculate_price(10.0, quantity=3)
        10.0
        >>> strategy.calculate_price(10.0, quantity=5)
        9.0
        >>> strategy.calculate_price(10.0, quantity=10)
        9.0
    """
    
    def __init__(self, min_quantity: int = 5, discount_percentage: float = 10.0):
        """
        Initialize strategy with discount for larger quantity.
        
        Args:
            min_quantity: Minimum quantity for discount
            discount_percentage: Discount percentage
            
        Examples:
            >>> strategy = BulkDiscountStrategy()
            >>> strategy.min_quantity
            5
            >>> strategy.discount_percentage
            10.0
        """
        self.min_quantity = min_quantity
        self.discount_percentage = discount_percentage
    
    def calculate_price(self, base_price: float, quantity: int = 1) -> float:
        """
        Calculate price with bulk discount if applicable.
        
        Args:
            base_price: Base price per item
            quantity: Number of items ordered
            
        Returns:
            Price per item (with discount if quantity >= min_quantity)
            
        Examples:
            >>> strategy = BulkDiscountStrategy(min_quantity=5, discount_percentage=10.0)
            >>> strategy.calculate_price(10.0, 4)
            10.0
            >>> strategy.calculate_price(10.0, 5)
            9.0
        """
        if quantity >= self.min_quantity:
            discount = base_price * (self.discount_percentage / 100)
            return base_price - discount
        return base_price


if __name__ == "__main__":
    import doctest
    print("Running doctest for pricing_strategy.py...")
    result = doctest.testmod(verbose=True)
    if result.failed == 0:
        print(f"\n✅ All {result.attempted} doctests passed!")
    else:
        print(f"\n❌ {result.failed} out of {result.attempted} doctests failed!")
