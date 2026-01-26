"""
Service for managing orders with asynchronous processing.
Uses asyncio for parallel order processing.
"""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from decorators.logging_decorators import log_async_calls, catch_async_exceptions


class OrderStatus(Enum):
    """Order status."""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Represents a single order."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    beverage_name: str = ""
    quantity: int = 1
    price: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    processing_time: float = 0.0
    
    def __str__(self):
        return f"Order({self.id}, {self.beverage_name} x{self.quantity}, {self.status.value})"


class OrderService:
    """Service for asynchronous order processing."""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
    
    @log_async_calls
    @catch_async_exceptions(default_return=None)
    async def create_order(
        self, 
        beverage_name: str, 
        quantity: int = 1, 
        price: float = 0.0,
        processing_time: float = 3.0
    ) -> Order:
        """
        Creates a new order and starts its processing.
        
        Args:
            beverage_name: Beverage name
            quantity: Quantity
            price: Price
            processing_time: Processing time in seconds (simulation)
            
        Returns:
            Created Order object
        """
        order = Order(
            beverage_name=beverage_name,
            quantity=quantity,
            price=price,
            processing_time=processing_time
        )
        
        self.orders[order.id] = order
        
        # Create asyncio task for order processing
        task = asyncio.create_task(self._process_order(order))
        self.active_tasks[order.id] = task
        
        print(f"✓ Created {order}")
        return order
    
    async def _process_order(self, order: Order):
        """
        Asynchronously processes order.
        Simulates different processing stages.
        """
        try:
            # Stage 1: Processing
            order.status = OrderStatus.PROCESSING
            print(f"⚙️  Processing {order}...")
            
            # Processing simulation (e.g. beverage preparation)
            await asyncio.sleep(order.processing_time)
            
            # Stage 2: Ready
            order.status = OrderStatus.READY
            print(f"✅ Ready {order}")
            
            # Simulation of waiting to be picked up
            await asyncio.sleep(1.0)
            
            # Stage 3: Completed
            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.now()
            print(f"🎉 Completed {order}")
            
        except asyncio.CancelledError:
            order.status = OrderStatus.CANCELLED
            print(f"❌ Cancelled {order}")
        finally:
            # Remove task from active tasks
            if order.id in self.active_tasks:
                del self.active_tasks[order.id]
    
    @log_async_calls
    @catch_async_exceptions(default_return=False)
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancels order if still processing.
        
        Args:
            order_id: Order ID
            
        Returns:
            True if order was cancelled, False otherwise
        """
        if order_id in self.active_tasks:
            task = self.active_tasks[order_id]
            task.cancel()
            
            # Wait for task to finish
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            return True
        return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Returns order by ID."""
        return self.orders.get(order_id)
    
    def get_all_orders(self) -> List[Order]:
        """Returns all orders."""
        return list(self.orders.values())
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Returns orders with specific status."""
        return [o for o in self.orders.values() if o.status == status]
    
    def get_active_order_count(self) -> int:
        """Returns number of active (processing) orders."""
        return len(self.active_tasks)
    
    async def wait_for_all_orders(self):
        """Waits for all orders to complete processing."""
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)
    
    def clear_completed_orders(self):
        """Deletes all completed orders."""
        completed_ids = [
            order_id for order_id, order in self.orders.items()
            if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]
        ]
        for order_id in completed_ids:
            del self.orders[order_id]
        return len(completed_ids)


# Demo functions

async def demo_parallel_processing():
    """Demo of parallel processing of multiple orders."""
    print("=== Demo: Parallel order processing ===\n")
    
    service = OrderService()
    
    # Create multiple orders at once
    print("Creating multiple orders...")
    orders = await asyncio.gather(
        service.create_order("Coffee", 2, 5.00, processing_time=3.0),
        service.create_order("Tea", 1, 2.00, processing_time=2.0),
        service.create_order("Beer", 3, 10.50, processing_time=4.0),
        service.create_order("Coffee", 1, 2.50, processing_time=2.5),
    )
    
    print(f"\n📊 Active orders: {service.get_active_order_count()}\n")
    
    # Wait a bit then check status
    await asyncio.sleep(1.5)
    print("\n--- Status after 1.5 seconds ---")
    for order in service.get_all_orders():
        print(f"  {order}")
    
    # Wait for all to complete
    print("\n⏳ Waiting for all orders to complete...\n")
    await service.wait_for_all_orders()
    
    print("\n--- Final status ---")
    for status in OrderStatus:
        orders_with_status = service.get_orders_by_status(status)
        if orders_with_status:
            print(f"{status.value}: {len(orders_with_status)} orders")


async def demo_cancel_order():
    """Demo of order cancellation."""
    print("\n\n=== Demo: Order cancellation ===\n")
    
    service = OrderService()
    
    # Create order with long processing time
    order1 = await service.create_order("Coffee", 1, 2.50, processing_time=5.0)
    order2 = await service.create_order("Tea", 1, 2.00, processing_time=3.0)
    
    # Wait a bit
    await asyncio.sleep(1.0)
    
    # Cancel first order
    print(f"\n🚫 Cancelling order {order1.id}...")
    cancelled = await service.cancel_order(order1.id)
    print(f"Cancellation {'successful' if cancelled else 'failed'}\n")
    
    # Wait for others
    await service.wait_for_all_orders()
    
    print("\n--- Final status ---")
    for order in service.get_all_orders():
        print(f"  {order}")


async def demo_real_time_monitoring():
    """Demo of real-time order status monitoring."""
    print("\n\n=== Demo: Real-time monitoring ===\n")
    
    service = OrderService()
    
    # Create orders
    await service.create_order("Coffee", 1, 2.50, processing_time=4.0)
    await service.create_order("Beer", 2, 7.00, processing_time=6.0)
    await service.create_order("Tea", 1, 2.00, processing_time=3.0)
    
    print("\n📊 Monitoring orders...\n")
    
    # Monitor status every 1 second
    for i in range(8):
        await asyncio.sleep(1.0)
        pending = len(service.get_orders_by_status(OrderStatus.PENDING))
        processing = len(service.get_orders_by_status(OrderStatus.PROCESSING))
        ready = len(service.get_orders_by_status(OrderStatus.READY))
        completed = len(service.get_orders_by_status(OrderStatus.COMPLETED))
        
        print(f"[{i+1}s] Pending: {pending}, Processing: {processing}, "
              f"Ready: {ready}, Completed: {completed}")
    
    await service.wait_for_all_orders()


def main():
    """Runs all demo functions."""
    asyncio.run(demo_parallel_processing())
    asyncio.run(demo_cancel_order())
    asyncio.run(demo_real_time_monitoring())


if __name__ == '__main__':
    main()
