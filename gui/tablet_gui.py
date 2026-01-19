import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import threading
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.order_service import OrderService, OrderStatus
from models.factory import BeverageFactory
from models.beverage import Coffee, Tea, Beer
from exporters.csv_exporter import CSVExporter
from exporters.pdf_exporter import PDFExporter


class TabletGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("☕ Modern Ordering Application")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f5f5f5')
        
        # Modern color scheme
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#16a085',
            'light': '#ecf0f1',
            'dark': '#34495e',
            'bg': '#f5f5f5',
            'card': '#ffffff'
        }
        
        # OrderService instance
        self.order_service = OrderService()
        
        # CSV Exporter instance
        self.csv_exporter = CSVExporter("izvjestaji")
        
        # PDF Exporter instance
        self.pdf_exporter = PDFExporter("izvjestaji")
        
        # Mapping GUI names to beverage classes
        self.beverage_mapping = {
            "Espresso": "Espresso",
            "Coffee": "Coffee",
            "Cappuccino": "Cappuccino",
            "Latte": "Latte",
            "Tea": "Tea",
            "Beer": "Beer",
            "Wine": "Wine",
            "Coca Cola": "CocaCola",
            "Juice": "Juice",
            "Water": "Water"
        }
        
        # Preparation times per beverage type (in seconds)
        self.preparation_times = {
            "Espresso": 2.0,
            "Coffee": 5.0,
            "Cappuccino": 6.0,
            "Latte": 6.5,
            "Tea": 3.0,
            "Beer": 1.5,
            "Wine": 2.0,
            "CocaCola": 1.0,
            "Juice": 1.5,
            "Water": 0.5
        }
        
        # Asyncio event loop in background
        self.loop = None
        self.loop_thread = None
        self._start_async_loop()
        
        # Main container
        main_container = tk.Frame(root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left side - order form
        left_frame = tk.Frame(
            main_container, 
            bg=self.colors['card'],
            relief=tk.FLAT,
            highlightbackground=self.colors['light'],
            highlightthickness=2
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Left side title
        title_frame = tk.Frame(left_frame, bg=self.colors['primary'], height=80)
        title_frame.pack(fill=tk.X, pady=0)
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame, 
            text="🛒 New Order", 
            font=("Segoe UI", 20, "bold"),
            bg=self.colors['primary'],
            fg='white'
        ).pack(pady=25)
        
        # Content frame with padding
        content_frame = tk.Frame(left_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Dropdown for beverage selection
        tk.Label(
            content_frame, 
            text="Select Beverage", 
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['card'],
            fg=self.colors['dark']
        ).pack(pady=(0, 8), anchor=tk.W)
        self.pice_var = tk.StringVar()
        
        # Style for combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Modern.TCombobox',
            fieldbackground=self.colors['light'],
            background='white',
            borderwidth=0,
            relief='flat'
        )
        
        self.pice_dropdown = ttk.Combobox(
            content_frame, 
            textvariable=self.pice_var,
            values=list(self.beverage_mapping.keys()),
            state="readonly",
            font=("Segoe UI", 12),
            width=28,
            style='Modern.TCombobox'
        )
        self.pice_dropdown.pack(pady=(0, 20))
        self.pice_dropdown.current(0)  # Select first element
        
        # Quantity field
        tk.Label(
            content_frame, 
            text="Quantity", 
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['card'],
            fg=self.colors['dark']
        ).pack(pady=(0, 8), anchor=tk.W)
        
        self.kolicina_entry = tk.Entry(
            content_frame, 
            font=("Segoe UI", 12),
            width=30,
            relief=tk.FLAT,
            bg=self.colors['light'],
            highlightbackground=self.colors['secondary'],
            highlightcolor=self.colors['secondary'],
            highlightthickness=2
        )
        self.kolicina_entry.insert(0, "1")  # Default quantity
        self.kolicina_entry.pack(pady=(0, 30), ipady=8)
        
        # "Order" button
        self.naruci_button = tk.Button(
            content_frame,
            text="✓ Place Order",
            font=("Segoe UI", 13, "bold"),
            bg=self.colors['success'],
            fg="white",
            relief=tk.FLAT,
            padx=50,
            pady=15,
            cursor="hand2",
            activebackground='#229954',
            activeforeground='white',
            command=self.on_naruchi_click
        )
        self.naruci_button.pack(pady=(0, 15), fill=tk.X)
        
        # "Export CSV Report" button
        self.csv_export_button = tk.Button(
            content_frame,
            text="📊 Export CSV",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['info'],
            fg="white",
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor="hand2",
            activebackground='#138d75',
            activeforeground='white',
            command=self.on_csv_export_click
        )
        self.csv_export_button.pack(pady=(0, 10), fill=tk.X)
        
        # "Export PDF Report" button
        self.pdf_export_button = tk.Button(
            content_frame,
            text="📄 Export PDF",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['secondary'],
            fg="white",
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor="hand2",
            activebackground='#2874a6',
            activeforeground='white',
            command=self.on_pdf_export_click
        )
        self.pdf_export_button.pack(pady=0, fill=tk.X)
        
        # Right side - order display
        right_frame = tk.Frame(
            main_container, 
            bg=self.colors['card'],
            relief=tk.FLAT,
            highlightbackground=self.colors['light'],
            highlightthickness=2
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Right side title
        title_frame_right = tk.Frame(right_frame, bg=self.colors['primary'], height=80)
        title_frame_right.pack(fill=tk.X, pady=0)
        title_frame_right.pack_propagate(False)
        tk.Label(
            title_frame_right, 
            text="📋 Active Orders", 
            font=("Segoe UI", 20, "bold"),
            bg=self.colors['primary'],
            fg='white'
        ).pack(pady=25)
        
        # Treeview for tabular display of orders
        tree_container = tk.Frame(right_frame, bg=self.colors['card'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Style for Treeview
        style.configure(
            "Modern.Treeview",
            background=self.colors['light'],
            foreground=self.colors['dark'],
            fieldbackground=self.colors['light'],
            rowheight=35,
            font=('Segoe UI', 10)
        )
        style.configure(
            "Modern.Treeview.Heading",
            font=('Segoe UI', 11, 'bold'),
            background=self.colors['dark'],
            foreground='white',
            relief=tk.FLAT
        )
        style.map('Modern.Treeview', background=[('selected', self.colors['secondary'])])
        
        columns = ("ID", "Beverage", "Quantity", "Price", "Status", "Time")
        self.narudzbe_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=20,
            style="Modern.Treeview"
        )
        
        # Setting headers
        self.narudzbe_tree.heading("ID", text="ID")
        self.narudzbe_tree.heading("Beverage", text="Beverage")
        self.narudzbe_tree.heading("Quantity", text="Quantity")
        self.narudzbe_tree.heading("Price", text="Price")
        self.narudzbe_tree.heading("Status", text="Status")
        self.narudzbe_tree.heading("Time", text="Time")
        
        # Setting column widths
        self.narudzbe_tree.column("ID", width=60, anchor=tk.CENTER)
        self.narudzbe_tree.column("Beverage", width=120, anchor=tk.W)
        self.narudzbe_tree.column("Quantity", width=80, anchor=tk.CENTER)
        self.narudzbe_tree.column("Price", width=80, anchor=tk.CENTER)
        self.narudzbe_tree.column("Status", width=110, anchor=tk.CENTER)
        self.narudzbe_tree.column("Time", width=90, anchor=tk.CENTER)
        
        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.narudzbe_tree.yview)
        self.narudzbe_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack Treeview and scrollbar
        self.narudzbe_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure colors for tags with modern palette
        self.narudzbe_tree.tag_configure('pending', background='#fff3cd', foreground='#856404')
        self.narudzbe_tree.tag_configure('processing', background='#cce5ff', foreground='#004085')
        self.narudzbe_tree.tag_configure('ready', background='#d4edda', foreground='#155724')
        self.narudzbe_tree.tag_configure('completed', background='#e2e3e5', foreground='#383d41')
        self.narudzbe_tree.tag_configure('cancelled', background='#f8d7da', foreground='#721c24')
        
        # Start periodic GUI update
        self.update_gui()
        
        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _start_async_loop(self):
        """Starts asyncio event loop in a separate thread."""
        def run_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=run_loop, args=(self.loop,), daemon=True)
        self.loop_thread.start()
    
    def on_naruchi_click(self):
        """Handler for 'Order' button click."""
        # Input validation
        pice_gui_name = self.pice_var.get()
        if not pice_gui_name:
            messagebox.showwarning("Warning", "Please select a beverage!")
            return
        
        try:
            kolicina = int(self.kolicina_entry.get())
            if kolicina <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Warning", "Quantity must be a positive number!")
            return
        
        # Map to beverage class
        beverage_name = self.beverage_mapping.get(pice_gui_name, pice_gui_name)
        
        # Get preparation time
        prep_time = self.preparation_times.get(beverage_name, 3.0)
        
        # Calculate price
        try:
            beverage = BeverageFactory.create(beverage_name)
            price = beverage.price() * kolicina
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create beverage: {e}")
            return
        
        # Create order asynchronously (doesn't block GUI)
        asyncio.run_coroutine_threadsafe(
            self.order_service.create_order(
                beverage_name=pice_gui_name,
                quantity=kolicina,
                price=price,
                processing_time=prep_time
            ),
            self.loop
        )
        
        # Clear fields
        self.kolicina_entry.delete(0, tk.END)
        self.kolicina_entry.insert(0, "1")
        
        # User feedback
        messagebox.showinfo("Success", f"Order sent!\n{pice_gui_name} x{kolicina}")
    
    def on_csv_export_click(self):
        """Handler for 'Export CSV' button click."""
        orders = self.order_service.get_all_orders()
        
        if not orders:
            messagebox.showwarning("Warning", "No orders to export!")
            return
        
        # Open dialog for report type selection
        export_type = messagebox.askquestion(
            "Report Type",
            "Do you want to save a daily report with statistics?\n\n"
            "Yes = Daily report with statistics\n"
            "No = Simple order list",
            icon='question'
        )
        
        try:
            if export_type == 'yes':
                # Daily report
                filepath = self.csv_exporter.export_daily_report(orders)
                report_type = "Daily CSV report"
            else:
                # Simple list
                filepath = self.csv_exporter.export_orders(orders)
                report_type = "CSV order list"
            
            # Success message
            messagebox.showinfo(
                "Success",
                f"{report_type} saved successfully!\n\n"
                f"Location: {filepath}\n"
                f"Number of orders: {len(orders)}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving CSV:\n{str(e)}")
    
    def on_pdf_export_click(self):
        """Handler for 'Export PDF' button click."""
        orders = self.order_service.get_all_orders()
        
        if not orders:
            messagebox.showwarning("Warning", "No orders to export!")
            return
        
        try:
            # Generate PDF report (always with full statistics)
            filepath = self.pdf_exporter.export_daily_report(orders)
            
            # Success message
            messagebox.showinfo(
                "Success",
                f"PDF report saved successfully! ✓\n\n"
                f"Location: {filepath}\n"
                f"Number of orders: {len(orders)}\n\n"
                f"Report includes:\n"
                f"• Overall statistics\n"
                f"• Statistics per beverage\n"
                f"• Detailed order list"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving PDF:\n{str(e)}")
    
    def update_gui(self):
        """Periodically updates the order display in the GUI."""
        # Clear current display
        for item in self.narudzbe_tree.get_children():
            self.narudzbe_tree.delete(item)
        
        # Add all orders
        for order in self.order_service.get_all_orders():
            time_str = order.created_at.strftime("%H:%M:%S")
            
            # Select status color
            status_text = order.status.value.upper()
            tags = ()
            
            if order.status == OrderStatus.PENDING:
                tags = ('pending',)
            elif order.status == OrderStatus.PROCESSING:
                tags = ('processing',)
            elif order.status == OrderStatus.READY:
                tags = ('ready',)
            elif order.status == OrderStatus.COMPLETED:
                tags = ('completed',)
            elif order.status == OrderStatus.CANCELLED:
                tags = ('cancelled',)
            
            self.narudzbe_tree.insert(
                "",
                tk.END,
                values=(
                    order.id,
                    order.beverage_name,
                    order.quantity,
                    f"{order.price:.2f}€",
                    status_text,
                    time_str
                ),
                tags=tags
            )
        
        # Repeat every 500ms
        self.root.after(500, self.update_gui)
    
    def on_closing(self):
        """Handler for window closing."""
        # Stop asyncio loop
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        # Close window
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TabletGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
