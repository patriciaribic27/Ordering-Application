"""
Unit tests for Order Service with async processing.
"""

import sys
from pathlib import Path

# Add parent directory to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from services.order_service import OrderService, Order, OrderStatus


class TestOrder:
    """Tests for Order class."""
    
    def test_order_creation(self):
        """Test basic order creation."""
        order = Order(
            beverage_name="Coffee",
            quantity=2,
            price=5.0
        )
        
        assert order.beverage_name == "Coffee"
        assert order.quantity == 2
        assert order.price == 5.0
        assert order.status == OrderStatus.PENDING
        assert order.created_at is not None
    
    def test_order_has_unique_id(self):
        """Test that each order has unique ID."""
        order1 = Order(beverage_name="Coffee", quantity=1, price=2.5)
        order2 = Order(beverage_name="Tea", quantity=1, price=2.0)
        
        assert order1.id != order2.id
    
    def test_order_status_transitions(self):
        """Test order status changes."""
        order = Order(beverage_name="Coffee", quantity=1, price=2.5)
        
        # Initial status
        assert order.status == OrderStatus.PENDING
        
        # Change to processing
        order.status = OrderStatus.PROCESSING
        assert order.status == OrderStatus.PROCESSING
        
        # Change to ready
        order.status = OrderStatus.READY
        assert order.status == OrderStatus.READY
        
        # Change to completed
        order.status = OrderStatus.COMPLETED
        assert order.status == OrderStatus.COMPLETED


class TestOrderService:
    """Tests for OrderService."""
    
    @pytest.fixture
    def order_service(self):
        """Create OrderService instance for testing."""
        return OrderService()
    
    @pytest.mark.asyncio
    async def test_create_order(self, order_service):
        """Test creating an order asynchronously."""
        order = await order_service.create_order(
            beverage_name="Coffee",
            quantity=1,
            price=2.5,
            processing_time=0.1  # Short time for test
        )
        
        assert order is not None
        assert order.beverage_name == "Coffee"
        assert order.quantity == 1
        assert order.price == 2.5
    
    @pytest.mark.asyncio
    async def test_order_processing_changes_status(self, order_service):
        """Test that order goes through status changes."""
        order = await order_service.create_order(
            beverage_name="Tea",
            quantity=1,
            price=2.0,
            processing_time=0.1
        )
        
        # Wait for processing to complete (longer wait)
        await asyncio.sleep(0.5)
        
        # Order should be ready or completed
        assert order.status in [OrderStatus.READY, OrderStatus.COMPLETED]
    
    @pytest.mark.asyncio
    async def test_get_all_orders(self, order_service):
        """Test retrieving all orders."""
        # Create multiple orders
        order1 = await order_service.create_order("Coffee", 1, 2.5, 0.1)
        order2 = await order_service.create_order("Tea", 2, 4.0, 0.1)
        
        # Get all orders
        orders = order_service.get_all_orders()
        
        assert len(orders) >= 2
        assert order1 in orders
        assert order2 in orders
    
    @pytest.mark.asyncio
    async def test_parallel_order_processing(self, order_service):
        """Test processing multiple orders in parallel."""
        # Create 3 orders simultaneously
        tasks = [
            order_service.create_order("Coffee", 1, 2.5, 0.1),
            order_service.create_order("Tea", 1, 2.0, 0.1),
            order_service.create_order("Beer", 1, 3.5, 0.1)
        ]
        
        orders = await asyncio.gather(*tasks)
        
        # All orders should be created
        assert len(orders) == 3
        
        # Wait for all to process
        await asyncio.sleep(0.5)
        
        # All should be ready or completed
        for order in orders:
            assert order.status in [OrderStatus.READY, OrderStatus.COMPLETED]
    
    @pytest.mark.asyncio
    async def test_order_with_zero_processing_time(self, order_service):
        """Test order with instant processing."""
        order = await order_service.create_order(
            beverage_name="Water",
            quantity=1,
            price=1.0,
            processing_time=0.0
        )
        
        # Should still go through all statuses
        await asyncio.sleep(0.05)
        assert order.status in [OrderStatus.READY, OrderStatus.COMPLETED]


class TestOrderIntegration:
    """Integration tests for order processing."""
    
    @pytest.fixture
    def order_service(self):
        """Create OrderService instance for testing."""
        return OrderService()
    
    @pytest.mark.asyncio
    async def test_multiple_services_independent(self):
        """Test that multiple OrderService instances are independent."""
        service1 = OrderService()
        service2 = OrderService()
        
        order1 = await service1.create_order("Coffee", 1, 2.5, 0.1)
        order2 = await service2.create_order("Tea", 1, 2.0, 0.1)
        
        # Each service should only have its own order
        assert order1 in service1.get_all_orders()
        assert order2 not in service1.get_all_orders()
        
        assert order2 in service2.get_all_orders()
        assert order1 not in service2.get_all_orders()
    
    @pytest.mark.asyncio
    async def test_order_performance(self, order_service):
        """Test that multiple orders don't block each other."""
        import time
        
        start_time = time.time()
        
        # Create 5 orders with 0.1s processing each
        tasks = [
            order_service.create_order(f"Beverage{i}", 1, 2.0, 0.1)
            for i in range(5)
        ]
        
        await asyncio.gather(*tasks)
        
        # Wait for processing
        await asyncio.sleep(0.15)
        
        elapsed = time.time() - start_time
        
        # Should take ~0.15s (parallel), not 0.5s (sequential)
        assert elapsed < 0.3  # Allow some overhead


class TestOrderCancellation:
    """Tests for order cancellation functionality."""
    
    @pytest.mark.asyncio
    async def test_cancel_order_in_processing(self):
        """Test cancelling order that is being processed."""
        service = OrderService()
        
        # Create order with long processing time
        order = await service.create_order("Coffee", 1, 2.5, processing_time=2.0)
        
        # Wait a bit for processing to start
        await asyncio.sleep(0.1)
        assert order.status == OrderStatus.PROCESSING
        
        # Cancel order
        result = await service.cancel_order(order.id)
        assert result is True
        assert order.status == OrderStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_order(self):
        """Test cancelling order that doesn't exist."""
        service = OrderService()
        
        result = await service.cancel_order("nonexistent_id")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cancel_completed_order(self):
        """Test that completed orders cannot be cancelled."""
        service = OrderService()
        
        # Create order with very short processing time
        order = await service.create_order("Coffee", 1, 2.5, processing_time=0.01)
        
        # Wait for completion (processing + ready + completed phases)
        await asyncio.sleep(1.5)
        assert order.status == OrderStatus.COMPLETED
        
        # Try to cancel - should return False (no active task)
        result = await service.cancel_order(order.id)
        assert result is False


class TestClearOrders:
    """Tests for clearing completed orders functionality."""
    
    @pytest.mark.asyncio
    async def test_clear_completed_orders(self):
        """Test clearing completed and cancelled orders."""
        service = OrderService()
        
        # Create several orders
        order1 = await service.create_order("Coffee", 1, 2.5, processing_time=0.01)
        order2 = await service.create_order("Tea", 1, 2.0, processing_time=0.01)
        order3 = await service.create_order("Beer", 1, 3.5, processing_time=0.5)
        
        # Wait for first two to complete (processing + ready + completed)
        await asyncio.sleep(1.5)
        
        # Cancel the third one
        await service.cancel_order(order3.id)
        
        # Should have 2 completed + 1 cancelled
        assert order1.status == OrderStatus.COMPLETED
        assert order2.status == OrderStatus.COMPLETED
        assert order3.status == OrderStatus.CANCELLED
        
        # Clear completed/cancelled
        count = service.clear_completed_orders()
        assert count == 3
        
        # All should be removed
        assert len(service.get_all_orders()) == 0
    
    def test_clear_with_no_completed_orders(self):
        """Test clearing when there are no completed orders."""
        service = OrderService()
        
        count = service.clear_completed_orders()
        assert count == 0
    
    @pytest.mark.asyncio
    async def test_clear_preserves_active_orders(self):
        """Test that clear only removes completed/cancelled orders."""
        service = OrderService()
        
        # Create mix of orders
        order1 = await service.create_order("Coffee", 1, 2.5, processing_time=0.01)
        order2 = await service.create_order("Tea", 1, 2.0, processing_time=2.0)  # Still processing
        
        # Wait for first to complete
        await asyncio.sleep(1.5)
        
        # Order1 should be completed, order2 still processing
        assert order1.status == OrderStatus.COMPLETED
        assert order2.status == OrderStatus.PROCESSING
        
        # Clear completed
        count = service.clear_completed_orders()
        assert count == 1
        
        # Only active order should remain
        remaining = service.get_all_orders()
        assert len(remaining) == 1
        assert remaining[0].id == order2.id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
