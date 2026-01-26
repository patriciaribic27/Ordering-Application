"""
CSV Exporter for order reports.
Enables export of daily reports in CSV format.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List
from services.order_service import Order, OrderStatus


class CSVExporter:
    """Exporter for CSV format reports."""
    
    def __init__(self, export_dir: str = "reports"):
        """
        Initialize CSV exporter.
        
        Args:
            export_dir: Directory where reports will be saved
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
    
    def export_orders(self, orders: List[Order], filename: str = None) -> str:
        """
        Export orders to CSV file.
        
        Args:
            orders: List of orders to export
            filename: File name (if not provided, generated automatically)
            
        Returns:
            Full path to created file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"orders_{timestamp}.csv"
        
        filepath = self.export_dir / filename
        
        # Prepare data
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ID', 'Beverage', 'Quantity', 'Price (EUR)', 'Status', 
                         'Created Time', 'Completed Time', 'Processing Duration (s)']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for order in orders:
                completed_time = ""
                duration = ""
                
                if order.completed_at:
                    completed_time = order.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                    duration = f"{(order.completed_at - order.created_at).total_seconds():.2f}"
                
                writer.writerow({
                    'ID': order.id,
                    'Beverage': order.beverage_name,
                    'Quantity': order.quantity,
                    'Price (EUR)': f"{order.price:.2f}",
                    'Status': order.status.value,
                    'Created Time': order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'Completed Time': completed_time,
                    'Processing Duration (s)': duration
                })
        
        return str(filepath)
    
    def export_daily_report(self, orders: List[Order]) -> str:
        """
        Export daily report with statistics.
        
        Args:
            orders: List of all orders
            
        Returns:
            Full path to created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"daily_report_{timestamp}.csv"
        filepath = self.export_dir / filename
        
        # Calculate statistics
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == OrderStatus.COMPLETED])
        cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
        total_revenue = sum(o.price for o in orders if o.status == OrderStatus.COMPLETED)
        
        # Statistics per beverage
        beverage_stats = {}
        for order in orders:
            if order.beverage_name not in beverage_stats:
                beverage_stats[order.beverage_name] = {
                    'quantity': 0,
                    'revenue': 0.0,
                    'count': 0
                }
            beverage_stats[order.beverage_name]['count'] += 1
            beverage_stats[order.beverage_name]['quantity'] += order.quantity
            if order.status == OrderStatus.COMPLETED:
                beverage_stats[order.beverage_name]['revenue'] += order.price
        
        # Save report
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['DAILY ORDER REPORT'])
            writer.writerow(['Date:', datetime.now().strftime("%Y-%m-%d")])
            writer.writerow(['Generated:', datetime.now().strftime("%H:%M:%S")])
            writer.writerow([])
            
            # Overall statistics
            writer.writerow(['OVERALL STATISTICS'])
            writer.writerow(['Total orders:', total_orders])
            writer.writerow(['Completed orders:', completed_orders])
            writer.writerow(['Cancelled orders:', cancelled_orders])
            writer.writerow(['Total revenue:', f"{total_revenue:.2f} EUR"])
            writer.writerow([])
            
            # Statistics per beverage
            writer.writerow(['STATISTICS PER BEVERAGE'])
            writer.writerow(['Beverage', 'Number of Orders', 'Total Quantity', 'Revenue (EUR)'])
            
            for beverage, stats in sorted(beverage_stats.items(), 
                                         key=lambda x: x[1]['revenue'], 
                                         reverse=True):
                writer.writerow([
                    beverage,
                    stats['count'],
                    stats['quantity'],
                    f"{stats['revenue']:.2f}"
                ])
            
            writer.writerow([])
            writer.writerow(['DETAILED ORDERS'])
            writer.writerow(['ID', 'Beverage', 'Quantity', 'Price (EUR)', 'Status', 
                           'Time', 'Duration (s)'])
            
            # All orders
            for order in sorted(orders, key=lambda x: x.created_at):
                duration = ""
                if order.completed_at:
                    duration = f"{(order.completed_at - order.created_at).total_seconds():.2f}"
                
                writer.writerow([
                    order.id,
                    order.beverage_name,
                    order.quantity,
                    f"{order.price:.2f}",
                    order.status.value,
                    order.created_at.strftime("%H:%M:%S"),
                    duration
                ])
        
        return str(filepath)
    
    def export_summary(self, orders: List[Order]) -> str:
        """
        Export summary report with statistics only.
        
        Args:
            orders: List of orders
            
        Returns:
            Full path to created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.csv"
        filepath = self.export_dir / filename
        
        # Statistics per beverage
        beverage_stats = {}
        for order in orders:
            if order.beverage_name not in beverage_stats:
                beverage_stats[order.beverage_name] = {
                    'quantity': 0,
                    'revenue': 0.0
                }
            beverage_stats[order.beverage_name]['quantity'] += order.quantity
            if order.status == OrderStatus.COMPLETED:
                beverage_stats[order.beverage_name]['revenue'] += order.price
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Beverage', 'Total Quantity', 'Revenue (EUR)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for beverage, stats in sorted(beverage_stats.items(), 
                                         key=lambda x: x[1]['revenue'], 
                                         reverse=True):
                writer.writerow({
                    'Beverage': beverage,
                    'Total Quantity': stats['quantity'],
                    'Revenue (EUR)': f"{stats['revenue']:.2f}"
                })
        
        return str(filepath)


# Demo functions

def demo():
    """CSV exporter demo."""
    from services.order_service import Order, OrderStatus
    from datetime import datetime, timedelta
    
    print("=== CSV Exporter Demo ===\n")
    
    # Create test orders
    orders = [
        Order(id="001", beverage_name="Coffee", quantity=2, price=5.00, 
              status=OrderStatus.COMPLETED, 
              created_at=datetime.now() - timedelta(hours=2),
              completed_at=datetime.now() - timedelta(hours=1, minutes=55)),
        Order(id="002", beverage_name="Tea", quantity=1, price=2.00,
              status=OrderStatus.COMPLETED,
              created_at=datetime.now() - timedelta(hours=1),
              completed_at=datetime.now() - timedelta(minutes=57)),
        Order(id="003", beverage_name="Beer", quantity=3, price=10.50,
              status=OrderStatus.COMPLETED,
              created_at=datetime.now() - timedelta(minutes=30),
              completed_at=datetime.now() - timedelta(minutes=28)),
        Order(id="004", beverage_name="Coffee", quantity=1, price=2.50,
              status=OrderStatus.PROCESSING,
              created_at=datetime.now() - timedelta(minutes=5)),
        Order(id="005", beverage_name="Juice", quantity=2, price=5.60,
              status=OrderStatus.CANCELLED,
              created_at=datetime.now() - timedelta(minutes=10)),
    ]
    
    exporter = CSVExporter()
    
    # Export all orders
    print("1. Exporting all orders...")
    file1 = exporter.export_orders(orders)
    print(f"   ✓ Saved to: {file1}\n")
    
    # Export daily report
    print("2. Exporting daily report...")
    file2 = exporter.export_daily_report(orders)
    print(f"   ✓ Saved to: {file2}\n")
    
    # Export summary
    print("3. Exporting summary...")
    file3 = exporter.export_summary(orders)
    print(f"   ✓ Saved to: {file3}\n")
    
    print(f"All files saved in '{exporter.export_dir}' directory")


if __name__ == '__main__':
    demo()
