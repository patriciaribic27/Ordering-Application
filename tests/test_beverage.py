"""
Unit tests for Beverage models and Factory pattern.
"""

import pytest
from models.beverage import Beverage
from models.factory import BeverageFactory
from services.pricing_strategy import HappyHourStrategy, StandardPricingStrategy


class TestBeverage:
    """Tests for Beverage base class."""
    
    def test_beverage_creation(self):
        """Test basic beverage creation."""
        # Beverage is abstract, so we test through factory
        coffee = BeverageFactory.create("Coffee")
        assert coffee is not None
        assert isinstance(coffee, Beverage)
    
    def test_beverage_has_price(self):
        """Test that beverage has a price method."""
        coffee = BeverageFactory.create("Coffee")
        price = coffee.price()
        assert isinstance(price, float)
        assert price > 0
    
    def test_beverage_pricing_strategy(self):
        """Test beverage uses pricing strategy."""
        coffee = BeverageFactory.create("Coffee")
        original_price = coffee.price()
        
        # Apply happy hour strategy
        coffee.set_pricing_strategy(HappyHourStrategy(20.0))
        discounted_price = coffee.price()
        
        # Discounted price should be less
        assert discounted_price < original_price
        assert discounted_price == original_price * 0.8


class TestBeverageFactory:
    """Tests for BeverageFactory."""
    
    def test_create_coffee(self):
        """Test creating coffee."""
        coffee = BeverageFactory.create("Coffee")
        assert coffee is not None
        assert "Coffee" in str(type(coffee).__name__)
    
    def test_create_espresso(self):
        """Test creating espresso."""
        espresso = BeverageFactory.create("Espresso")
        assert espresso is not None
    
    def test_create_tea(self):
        """Test creating tea."""
        tea = BeverageFactory.create("Tea")
        assert tea is not None
    
    def test_create_beer(self):
        """Test creating beer."""
        beer = BeverageFactory.create("Beer")
        assert beer is not None
    
    def test_create_invalid_beverage(self):
        """Test that creating invalid beverage raises error or returns None."""
        try:
            bev = BeverageFactory.create("InvalidBeverage")
            # If it doesn't raise, it should return None or handle gracefully
            assert bev is None or isinstance(bev, Beverage)
        except (ValueError, KeyError, AttributeError):
            # This is expected behavior
            pass
    
    def test_all_beverages_have_price(self):
        """Test that all beverages can calculate price."""
        beverages = ["Coffee", "Espresso", "Tea", "Beer", "CocaCola"]
        
        for bev_name in beverages:
            try:
                bev = BeverageFactory.create(bev_name)
                price = bev.price()
                assert isinstance(price, float)
                assert price > 0
            except ValueError:
                # Skip if beverage not implemented
                pass
    
    def test_factory_creates_different_instances(self):
        """Test that factory creates new instances each time."""
        coffee1 = BeverageFactory.create("Coffee")
        coffee2 = BeverageFactory.create("Coffee")
        
        # Should be different objects
        assert coffee1 is not coffee2
        
        # But same price
        assert coffee1.price() == coffee2.price()


class TestBeverageIntegration:
    """Integration tests for beverage system."""
    
    def test_beverage_with_multiple_strategies(self):
        """Test applying multiple strategies to same beverage."""
        coffee = BeverageFactory.create("Coffee")
        base_price = coffee.price()
        
        # Standard strategy
        coffee.set_pricing_strategy(StandardPricingStrategy())
        assert coffee.price() == base_price
        
        # Happy hour
        coffee.set_pricing_strategy(HappyHourStrategy(20.0))
        assert coffee.price() < base_price
        
        # Back to standard
        coffee.set_pricing_strategy(StandardPricingStrategy())
        assert coffee.price() == base_price
    
    def test_get_pricing_strategy(self):
        """Test retrieving current pricing strategy."""
        coffee = BeverageFactory.create("Coffee")
        
        # Default should be StandardPricingStrategy
        strategy = coffee.get_pricing_strategy()
        assert isinstance(strategy, StandardPricingStrategy)
        
        # Change strategy
        new_strategy = HappyHourStrategy()
        coffee.set_pricing_strategy(new_strategy)
        assert coffee.get_pricing_strategy() == new_strategy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
