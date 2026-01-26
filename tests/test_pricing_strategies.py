"""
Unit tests for pricing strategies.
Tests the Strategy Pattern implementation including PricingContext.
"""

import sys
from pathlib import Path

# Add parent directory to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch
from datetime import datetime
from services.pricing_strategy import (
    PricingContext,
    StandardPricingStrategy,
    HappyHourStrategy,
    BulkDiscountStrategy
)


class TestPricingContext:
    """Tests for PricingContext - the core of Strategy Pattern."""
    
    def test_context_default_strategy(self):
        """Test that context uses StandardPricingStrategy by default."""
        context = PricingContext()
        assert isinstance(context._strategy, StandardPricingStrategy)
        assert context.calculate(10.0, 1) == 10.0
    
    def test_context_with_initial_strategy(self):
        """Test creating context with initial strategy."""
        strategy = HappyHourStrategy(20.0)
        context = PricingContext(strategy)
        assert context._strategy == strategy
        assert context.calculate(10.0, 1) == 8.0  # 20% off
    
    def test_set_strategy_changes_behavior(self):
        """Test that set_strategy changes calculation behavior."""
        context = PricingContext(StandardPricingStrategy())
        assert context.calculate(10.0, 1) == 10.0
        
        # Change to Happy Hour
        context.set_strategy(HappyHourStrategy(20.0))
        assert context.calculate(10.0, 1) == 8.0
        
        # Change to Bulk Discount
        context.set_strategy(BulkDiscountStrategy(5, 10.0))
        assert context.calculate(10.0, 5) == 45.0
    
    def test_get_strategy_name(self):
        """Test getting strategy name."""
        context = PricingContext(StandardPricingStrategy())
        assert context.get_strategy_name() == "StandardPricingStrategy"
        
        context.set_strategy(HappyHourStrategy())
        assert context.get_strategy_name() == "HappyHourStrategy"
        
        context.set_strategy(BulkDiscountStrategy())
        assert context.get_strategy_name() == "BulkDiscountStrategy"
    
    def test_multiple_contexts_independently(self):
        """Test that multiple contexts work independently."""
        context1 = PricingContext(StandardPricingStrategy())
        context2 = PricingContext(HappyHourStrategy(50.0))
        context3 = PricingContext(BulkDiscountStrategy(5, 15.0))
        
        # Each should maintain its own strategy
        assert context1.calculate(10.0, 1) == 10.0
        assert context2.calculate(10.0, 1) == 5.0
        assert context3.calculate(10.0, 5) == 42.5


class TestStandardPricingStrategy:
    """Tests for StandardPricingStrategy."""
    
    def test_calculate_price_returns_base_price(self):
        """Test that standard strategy returns base price unchanged."""
        strategy = StandardPricingStrategy()
        assert strategy.calculate_price(10.0) == 10.0
        assert strategy.calculate_price(5.5) == 5.5
        assert strategy.calculate_price(0.0) == 0.0
    
    def test_calculate_price_with_various_prices(self):
        """Test standard pricing with various price points."""
        strategy = StandardPricingStrategy()
        test_prices = [1.0, 2.5, 10.99, 100.0, 999.99]
        for price in test_prices:
            assert strategy.calculate_price(price) == price


class TestHappyHourStrategy:
    """Tests for HappyHourStrategy."""
    
    def test_default_discount_is_20_percent(self):
        """Test that default discount is 20%."""
        strategy = HappyHourStrategy()
        base_price = 10.0
        expected = 8.0  # 20% off
        assert strategy.calculate_price(base_price) == expected
    
    def test_custom_discount_percentage(self):
        """Test happy hour with custom discount."""
        strategy = HappyHourStrategy(discount_percentage=30.0)
        base_price = 10.0
        expected = 7.0  # 30% off
        assert strategy.calculate_price(base_price) == expected
    
    def test_happy_hour_various_prices(self):
        """Test happy hour discount on various prices."""
        strategy = HappyHourStrategy(discount_percentage=20.0)
        
        # Test different prices
        assert strategy.calculate_price(5.0) == 4.0
        assert strategy.calculate_price(2.5) == 2.0
        assert pytest.approx(strategy.calculate_price(3.33), 0.01) == 2.664
    
    def test_zero_discount(self):
        """Test with 0% discount."""
        strategy = HappyHourStrategy(discount_percentage=0.0)
        assert strategy.calculate_price(10.0) == 10.0
    
    def test_full_discount(self):
        """Test with 100% discount (free)."""
        strategy = HappyHourStrategy(discount_percentage=100.0)
        assert strategy.calculate_price(10.0) == 0.0


class TestBulkDiscountStrategy:
    """Tests for BulkDiscountStrategy."""
    
    def test_default_bulk_discount(self):
        """Test bulk discount with defaults (5+ items, 10% off)."""
        strategy = BulkDiscountStrategy()
        
        # Below minimum - no discount
        assert strategy.calculate_price(10.0, quantity=1) == 10.0
        assert strategy.calculate_price(10.0, quantity=4) == 10.0
        
        # At or above minimum - discount applied
        assert strategy.calculate_price(10.0, quantity=5) == 9.0
        assert strategy.calculate_price(10.0, quantity=10) == 9.0
    
    def test_custom_bulk_parameters(self):
        """Test bulk discount with custom parameters."""
        strategy = BulkDiscountStrategy(min_quantity=3, discount_percentage=15.0)
        
        # Below minimum
        assert strategy.calculate_price(10.0, quantity=2) == 10.0
        
        # At or above minimum
        assert strategy.calculate_price(10.0, quantity=3) == 8.5
        assert strategy.calculate_price(10.0, quantity=5) == 8.5
    
    def test_no_quantity_defaults_to_one(self):
        """Test that omitting quantity defaults to 1."""
        strategy = BulkDiscountStrategy(min_quantity=1, discount_percentage=10.0)
        
        # Default quantity should be 1, which meets minimum
        result = strategy.calculate_price(10.0)
        assert result == 9.0
    
    def test_various_quantities(self):
        """Test bulk discount across various quantities."""
        strategy = BulkDiscountStrategy(min_quantity=5, discount_percentage=10.0)
        
        test_cases = [
            (10.0, 1, 10.0),   # No discount
            (10.0, 4, 10.0),   # No discount
            (10.0, 5, 9.0),    # Discount
            (10.0, 10, 9.0),   # Discount
            (5.0, 5, 4.5),     # Discount on different price
        ]
        
        for price, qty, expected in test_cases:
            assert strategy.calculate_price(price, qty) == expected


class TestStrategyIntegration:
    """Integration tests for pricing strategies."""
    
    def test_all_strategies_implement_interface(self):
        """Test that all strategies can calculate prices."""
        strategies = [
            StandardPricingStrategy(),
            HappyHourStrategy(),
            BulkDiscountStrategy()
        ]
        
        base_price = 10.0
        for strategy in strategies:
            result = strategy.calculate_price(base_price)
            assert isinstance(result, float)
            assert result >= 0
    
    def test_strategy_comparison(self):
        """Test comparing different strategies on same price."""
        base_price = 10.0
        
        standard = StandardPricingStrategy().calculate_price(base_price)
        happy_hour = HappyHourStrategy().calculate_price(base_price)
        bulk = BulkDiscountStrategy().calculate_price(base_price, 5)
        
        # Happy hour and bulk should be less than standard
        assert happy_hour < standard
        assert bulk < standard
        
        # Happy hour (20% off) should be cheaper than bulk (10% off)
        assert happy_hour < bulk


class TestAutomaticStrategySelection:
    """Tests for automatic time-based strategy selection."""
    
    def test_auto_select_during_happy_hour(self):
        """Test that auto_select=True selects HappyHourStrategy during 16:00-18:00."""
        # Mock time to 16:30 (during Happy Hour)
        mock_time = datetime.now().replace(hour=16, minute=30, second=0)
        
        with patch('services.pricing_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            
            context = PricingContext(auto_select=True)
            
            # Should use HappyHourStrategy
            assert isinstance(context._strategy, HappyHourStrategy)
            assert context.get_strategy_name() == "HappyHourStrategy"
            
            # Should apply 20% discount
            assert context.calculate(10.0, 1, log_calculation=False) == 8.0
    
    def test_auto_select_outside_happy_hour(self):
        """Test that auto_select=True selects StandardPricingStrategy outside 16:00-18:00."""
        # Mock time to 12:00 (outside Happy Hour)
        mock_time = datetime.now().replace(hour=12, minute=0, second=0)
        
        with patch('services.pricing_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            
            context = PricingContext(auto_select=True)
            
            # Should use StandardPricingStrategy
            assert isinstance(context._strategy, StandardPricingStrategy)
            assert context.get_strategy_name() == "StandardPricingStrategy"
            
            # Should not apply discount
            assert context.calculate(10.0, 1, log_calculation=False) == 10.0
    
    def test_auto_select_at_happy_hour_start(self):
        """Test strategy selection at exactly 16:00 (Happy Hour start)."""
        mock_time = datetime.now().replace(hour=16, minute=0, second=0)
        
        with patch('services.pricing_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            
            context = PricingContext(auto_select=True)
            assert isinstance(context._strategy, HappyHourStrategy)
    
    def test_auto_select_at_happy_hour_end(self):
        """Test strategy selection at exactly 18:00 (Happy Hour end)."""
        mock_time = datetime.now().replace(hour=18, minute=0, second=0)
        
        with patch('services.pricing_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            
            context = PricingContext(auto_select=True)
            # At 18:00, Happy Hour should be over
            assert isinstance(context._strategy, StandardPricingStrategy)
    
    def test_update_strategy_by_time(self):
        """Test that update_strategy_by_time() refreshes the strategy."""
        # Start with time outside Happy Hour
        mock_time_before = datetime.now().replace(hour=12, minute=0, second=0)
        
        with patch('services.pricing_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time_before
            
            context = PricingContext(auto_select=True)
            assert isinstance(context._strategy, StandardPricingStrategy)
            
            # Change time to during Happy Hour
            mock_time_after = datetime.now().replace(hour=17, minute=0, second=0)
            mock_datetime.now.return_value = mock_time_after
            
            # Update strategy
            context.update_strategy_by_time()
            
            # Should now use HappyHourStrategy
            assert isinstance(context._strategy, HappyHourStrategy)
    
    def test_manual_strategy_overrides_auto_select(self):
        """Test that manually setting strategy works even with auto_select."""
        mock_time = datetime.now().replace(hour=12, minute=0, second=0)
        
        with patch('services.pricing_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            
            # Create with auto_select (should be Standard)
            context = PricingContext(auto_select=True)
            assert isinstance(context._strategy, StandardPricingStrategy)
            
            # Manually set to HappyHour
            context.set_strategy(HappyHourStrategy(50.0))
            assert isinstance(context._strategy, HappyHourStrategy)
            
            # Should now use 50% discount
            assert context.calculate(10.0, 1, log_calculation=False) == 5.0
    
    def test_calculate_with_logging_disabled(self):
        """Test that log_calculation=False prevents logging."""
        context = PricingContext(StandardPricingStrategy())
        
        # Should not raise any errors with logging disabled
        result = context.calculate(10.0, 2, log_calculation=False)
        assert result == 20.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

