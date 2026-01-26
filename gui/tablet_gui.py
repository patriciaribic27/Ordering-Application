import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import threading
import sys
from pathlib import Path
from datetime import datetime
from aiohttp import web

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.order_service import OrderService, OrderStatus
from services.menu_service import MenuService
from services.api_server import create_app
from services.pricing_strategy import (
    PricingContext, 
    StandardPricingStrategy, 
    HappyHourStrategy, 
    BulkDiscountStrategy
)
from models.factory import BeverageFactory
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
        
        # MenuService instance for fetching menu from REST API
        self.menu_service = MenuService("http://localhost:8080")
        
        # CSV Exporter instance
        self.csv_exporter = CSVExporter("izvjestaji")
        
        # PDF Exporter instance
        self.pdf_exporter = PDFExporter("izvjestaji")
        
        # Menu cache from API
        self.menu_from_api = None
        self.api_server_running = False
        
        # Mapping GUI names to beverage classes
        # This maps API beverage names to Factory class names
        self.beverage_mapping = {
            "Espresso": "Espresso",
            "Coffee": "Coffee",
            "Cappuccino": "Cappuccino",
            "Latte": "Latte",
            "Tea": "Tea",
            "Beer": "Beer",
            "Wine": "Wine",
            "CocaCola": "CocaCola",  # API returns CocaCola
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
        self.api_server_task = None
        self._start_async_loop()
        
        # Start REST API server in background
        self._start_api_server()
        
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
            values=[],  # Will be populated from REST API
            state="readonly",
            font=("Segoe UI", 12),
            width=28,
            style='Modern.TCombobox'
        )
        self.pice_dropdown.pack(pady=(0, 20))
        # Don't select anything yet - wait for API response
        
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
        self.kolicina_entry.pack(pady=(0, 20), ipady=8)
        
        # Info frame for discounts
        info_frame = tk.Frame(content_frame, bg=self.colors['light'])
        info_frame.pack(pady=(0, 30), fill=tk.X)
        
        # Happy Hour info
        happy_hour_label = tk.Label(
            info_frame,
            text="Happy Hour (20% off) is automatically active 16:00-18:00",
            font=("Segoe UI", 9, "italic"),
            bg=self.colors['light'],
            fg=self.colors['dark'],
            wraplength=350,
            justify=tk.LEFT,
            padx=10
        )
        happy_hour_label.pack(fill=tk.X, pady=(10, 5))
        
        # Bulk discount info
        bulk_discount_label = tk.Label(
            info_frame,
            text="Bulk Discount (10% off) automatically applies to orders of 5+ items",
            font=("Segoe UI", 9, "italic"),
            bg=self.colors['light'],
            fg=self.colors['dark'],
            wraplength=350,
            justify=tk.LEFT,
            padx=10
        )
        bulk_discount_label.pack(fill=tk.X, pady=(0, 10))
        
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
        self.pdf_export_button.pack(pady=(0, 10), fill=tk.X)
        
        # "Clear Completed Orders" button
        self.clear_button = tk.Button(
            content_frame,
            text="🗑️ Clear Completed",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['warning'],
            fg="white",
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor="hand2",
            activebackground='#d68910',
            activeforeground='white',
            command=self.on_clear_completed_click
        )
        self.clear_button.pack(pady=0, fill=tk.X)
        
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
        
        # Status bar at the bottom
        status_frame = tk.Frame(right_frame, bg=self.colors['dark'], height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="🔄 Initializing...",
            font=("Segoe UI", 9),
            bg=self.colors['dark'],
            fg=self.colors['light'],
            anchor=tk.W
        )
        self.status_label.pack(padx=15, pady=10, fill=tk.X)
        
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
        
        # Right-click context menu for orders
        self.context_menu = tk.Menu(self.narudzbe_tree, tearoff=0)
        self.context_menu.add_command(label="❌ Cancel Order", command=self.on_cancel_order)
        
        # Bind right-click to show context menu
        self.narudzbe_tree.bind("<Button-3>", self.show_context_menu)
        
        # Configure colors for tags with modern palette
        self.narudzbe_tree.tag_configure('pending', background='#fff3cd', foreground='#856404')
        self.narudzbe_tree.tag_configure('processing', background='#cce5ff', foreground='#004085')
        self.narudzbe_tree.tag_configure('ready', background='#d4edda', foreground='#155724')
        self.narudzbe_tree.tag_configure('completed', background='#e2e3e5', foreground='#383d41')
        self.narudzbe_tree.tag_configure('cancelled', background='#f8d7da', foreground='#721c24')
        
        # Start periodic GUI update
        self.update_gui()
        
        # Schedule menu fetch after GUI is ready (delayed start)
        self.root.after(500, self._schedule_menu_fetch)
        
        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _schedule_menu_fetch(self):
        """Schedule async menu fetch after GUI is initialized."""
        asyncio.run_coroutine_threadsafe(
            self._fetch_menu_async(),
            self.loop
        )
    
    def _start_async_loop(self):
        """Starts asyncio event loop in a separate thread."""
        def run_loop(loop):
            asyncio.set_event_loop(loop)
            try:
                loop.run_forever()
            finally:
                loop.close()
        
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=run_loop, args=(self.loop,), daemon=True)
        self.loop_thread.start()
        
        # Give the loop thread a moment to start
        import time
        time.sleep(0.1)
    
    def _start_api_server(self):
        """Starts REST API server in background using asyncio."""
        async def run_api_server():
            try:
                app = create_app()
                runner = web.AppRunner(app)
                await runner.setup()
                site = web.TCPSite(runner, 'localhost', 8080)
                await site.start()
                self.api_server_running = True
                print("✓ REST API server started on http://localhost:8080")
                print("  Available endpoints:")
                print("    - GET /api/menu")
                print("    - GET /api/beverages/{id}")
                print("    - GET /health")
                
                # Keep server running
                while True:
                    await asyncio.sleep(3600)
            except OSError as e:
                if "address already in use" in str(e).lower():
                    print("⚠️  REST API server already running on port 8080")
                    self.api_server_running = True
                else:
                    print(f"❌ Failed to start REST API server: {e}")
            except Exception as e:
                print(f"❌ Error starting REST API server: {e}")
        
        # Start server in the asyncio loop
        future = asyncio.run_coroutine_threadsafe(
            run_api_server(),
            self.loop
        )
        self.api_server_task = future
    
    async def _fetch_menu_async(self):
        """Asynchronously fetches menu from REST API."""
        try:
            # Wait a moment for server to start
            await asyncio.sleep(0.5)
            
            print("\n" + "="*60)
            print("🌐 ASYNC REST API CALL: Fetching menu from server...")
            print("   URL: http://localhost:8080/api/menu")
            print("="*60)
            
            self._update_status("🔄 Fetching menu from REST API...")
            
            # Fetch menu from API (ASYNCHRONOUSLY!)
            # Make sure we're using the current event loop
            menu_data = await self.menu_service.fetch_menu()
            
            if menu_data:
                self.menu_from_api = menu_data
                beverages = menu_data.get('beverages', [])
                available_beverages = [b for b in beverages if b.get('available', True)]
                available_count = len(available_beverages)
                
                print("\n✅ REST API RESPONSE: Menu fetched successfully!")
                print(f"   📋 {available_count} beverages available")
                for bev in available_beverages:
                    print(f"      - {bev['name']}: {bev['base_price']} {bev['currency']}")
                print("="*60 + "\n")
                
                # Update dropdown with only available beverages from API
                self._update_dropdown_from_api(available_beverages)
                
                self._update_status(
                    f"✅ Menu loaded from API: {available_count} beverages available | "
                    f"API: http://localhost:8080"
                )
                
                print(f"\n✓ Menu fetched from REST API:")
                print(f"  Total beverages: {len(beverages)}")
                print(f"  Available: {available_count}")
                for bev in beverages:
                    status = "✓" if bev.get('available', True) else "✗"
                    print(f"    {status} {bev['name']}: {bev['base_price']}€")
            else:
                self._update_status("❌ Menu unavailable - Check connection")
                print("❌ CRITICAL: Could not fetch menu from API. Application requires REST API!")
                messagebox.showerror(
                    "Menu Loading Error",
                    "Cannot load beverage menu.\n\n"
                    "Please ensure the application is properly started\n"
                    "or contact technical support."
                )
        
        except Exception as e:
            self._update_status(f"❌ Error fetching menu: {e}")
            print(f"❌ Error fetching menu from API: {e}")
    
    def _update_status(self, message):
        """Updates status bar message (thread-safe)."""
        def update():
            if hasattr(self, 'status_label'):
                self.status_label.config(text=message)
        
        self.root.after(0, update)
    
    def _update_dropdown_from_api(self, beverages):
        """Updates the dropdown menu with beverages from API."""
        def update():
            if hasattr(self, 'pice_dropdown') and beverages:
                # Create display names with prices (e.g., "Espresso - 2.50€")
                display_names = [f"{bev['name']} - {bev['base_price']:.2f}€" for bev in beverages]
                
                # Update dropdown values
                self.pice_dropdown['values'] = display_names
                
                # Set first beverage as default
                if display_names:
                    self.pice_var.set(display_names[0])
        
        self.root.after(0, update)
    
    async def process_order(self, beverage_name: str, quantity: int, price: float, prep_time: float):
        """Asynchronously process order with status updates in GUI."""
        try:
            # Get current active count BEFORE creating new order
            active_before = self.order_service.get_active_order_count()
            
            print(f"⚡ PARALLEL PROCESSING: Current active orders: {active_before}")
            print(f"   Creating new async task for: {beverage_name} x{quantity}")
            
            # Create order in OrderService (async, non-blocking)
            # This uses asyncio.create_task() internally - TRUE PARALLELISM!
            order = await self.order_service.create_order(
                beverage_name=beverage_name,
                quantity=quantity,
                price=price,
                processing_time=prep_time
            )
            
            active_after = self.order_service.get_active_order_count()
            print(f"✓ Async task created! Active orders now: {active_after}")
            print(f"   All {active_after} orders are processing IN PARALLEL!\n")
            
            # Update GUI immediately - show "Sent" status
            self._update_order_in_tree(order)
            
            # Start monitoring order status changes
            await self._monitor_order_status(order.id)
            
        except Exception as e:
            print(f"❌ Error processing order: {e}")
    
    async def _monitor_order_status(self, order_id: str):
        """Monitor order status and update GUI accordingly."""
        while True:
            await asyncio.sleep(0.5)  # Check every 0.5 seconds
            
            order = self.order_service.orders.get(order_id)
            if not order:
                break
            
            # Update GUI with current status
            self._update_order_in_tree(order)
            
            # Stop monitoring only when fully completed or cancelled
            # Continue monitoring through READY state until COMPLETED
            if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
                break
    
    def _update_order_in_tree(self, order):
        """Update or insert order in treeview (thread-safe)."""
        def update():
            if not hasattr(self, 'narudzbe_tree'):
                return
            
            # Map status to display text
            status_map = {
                OrderStatus.PENDING: "Sent",
                OrderStatus.PROCESSING: "Processing",
                OrderStatus.READY: "Ready",
                OrderStatus.COMPLETED: "Completed",
                OrderStatus.CANCELLED: "Cancelled"
            }
            
            status_text = status_map.get(order.status, order.status.value)
            
            # Format time
            time_str = order.created_at.strftime("%H:%M:%S")
            
            # Check if order already exists in tree
            existing_item = None
            for item in self.narudzbe_tree.get_children():
                if self.narudzbe_tree.item(item)['values'][0] == order.id:
                    existing_item = item
                    break
            
            # Prepare values
            values = (
                order.id,
                order.beverage_name,
                order.quantity,
                f"{order.price:.2f}€",
                status_text,
                time_str
            )
            
            # Tag for coloring
            tag = order.status.value
            
            if existing_item:
                # Update existing
                self.narudzbe_tree.item(existing_item, values=values, tags=(tag,))
            else:
                # Insert new at top
                self.narudzbe_tree.insert('', 0, values=values, tags=(tag,))
            
            # Update status bar with PARALLEL PROCESSING info
            active_orders = len([o for o in self.order_service.get_all_orders() 
                                if o.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]])
            
            all_orders = self.order_service.get_all_orders()
            
            # Show parallel processing indicator
            if active_orders > 0:
                parallel_text = f"⚙️  Processing {active_orders} order(s) IN PARALLEL"
            else:
                parallel_text = "✓ Ready for orders"
            
            self.status_label.config(
                text=f"{parallel_text} | Total: {len(all_orders)} | API: http://localhost:8080"
            )
        
        self.root.after(0, update)
    
    def on_naruchi_click(self):
        """Handler for 'Order' button click."""
        # Input validation
        pice_gui_display = self.pice_var.get()
        if not pice_gui_display:
            messagebox.showwarning("Warning", "Please select a beverage!")
            return
        
        # Extract beverage name from display format "Name - Price€"
        pice_gui_name = pice_gui_display.split(" - ")[0] if " - " in pice_gui_display else pice_gui_display
        
        try:
            kolicina = int(self.kolicina_entry.get())
            if kolicina <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Warning", "Quantity must be a positive number!")
            return
        
        # ============================================================
        # FACTORY PATTERN: Create beverage using Factory
        # ============================================================
        # All beverages are created EXCLUSIVELY through BeverageFactory
        # This demonstrates proper Factory Pattern usage
        
        # Map GUI name to beverage class name
        beverage_name = self.beverage_mapping.get(pice_gui_name, pice_gui_name)
        
        # Create beverage object using Factory (REQUIRED)
        try:
            beverage_obj = BeverageFactory.create(beverage_name)
            print(f"🏭 Factory created: {beverage_obj.__class__.__name__}")
        except Exception as e:
            messagebox.showerror(
                "Creation Error",
                f"Cannot create beverage '{beverage_name}'.\n\n"
                f"Error: {e}"
            )
            return
        
        
        # ============================================================
        # GET PRICE FROM REST API (NOT from Factory!)
        # ============================================================
        # This demonstrates that prices come from REST API, not hardcoded
        
        # Try to get price from API menu first
        base_price = None
        if self.menu_from_api and 'beverages' in self.menu_from_api:
            for api_bev in self.menu_from_api['beverages']:
                if api_bev['name'] == beverage_name:
                    base_price = api_bev['base_price']
                    print(f"\n💰 PRICE FROM REST API: {beverage_name} = {base_price} EUR")
                    print(f"   (Fetched from http://localhost:8080/api/menu)")
                    break
        
        # Fallback to Factory price if API unavailable
        if base_price is None:
            base_price = beverage_obj.price()
            print(f"\n⚠️  API unavailable, using Factory price: {beverage_name} = {base_price} EUR")
        
        # Get preparation time
        prep_time = self.preparation_times.get(beverage_name, 3.0)
        
        # ============================================================
        # STRATEGY PATTERN: Determine pricing strategy dynamically
        # ============================================================
        # This demonstrates proper Strategy Pattern usage:
        # - Strategy is selected AUTOMATICALLY based on time (16:00-18:00 = Happy Hour)
        # - PricingContext encapsulates the strategy
        # - Centralized logic without GUI hardcoding
        # - Easy to add new strategies without modifying this code
        
        # Create pricing context with AUTOMATIC time-based strategy selection
        # This will automatically choose HappyHourStrategy during 16:00-18:00,
        # or StandardPricingStrategy at other times
        pricing_context = PricingContext(auto_select=True)
        
        # Check for bulk discount and prepare message
        discount_message = ""
        original_total = base_price * kolicina
        
        # Override with bulk discount if quantity is 5 or more
        if kolicina >= 5:
            bulk_strategy = BulkDiscountStrategy(min_quantity=5, discount_percentage=10.0)
            pricing_context.set_strategy(bulk_strategy)
            print(f"Bulk order detected ({kolicina} items), switching to BulkDiscountStrategy")
            discount_message = f"\n\nBULK DISCOUNT APPLIED!\n10% off for orders of 5+ items\nOriginal: {original_total:.2f} EUR"
        
        # Calculate final price using the strategy (working with Factory beverage)
        # Logging is automatically done inside calculate() method
        final_price = pricing_context.calculate(base_price, kolicina)
        
        # ============================================================
        
        # Create order asynchronously using create_task (non-blocking)
        print(f"\n🚀 ASYNC ORDER CREATED: {pice_gui_name} x{kolicina}")
        print(f"   Processing will happen in PARALLEL (non-blocking)")
        print(f"   You can continue ordering while this processes!\n")
        
        asyncio.run_coroutine_threadsafe(
            self.process_order(
                beverage_name=pice_gui_name,
                quantity=kolicina,
                price=final_price,
                prep_time=prep_time
            ),
            self.loop
        )
        
        # Clear fields
        self.kolicina_entry.delete(0, tk.END)
        self.kolicina_entry.insert(0, "1")
        
        # User feedback - order sent (non-blocking)
        messagebox.showinfo(
            "Success", 
            f"Order sent!\n{pice_gui_name} x{kolicina}\nFinal Price: {final_price:.2f} EUR{discount_message}"
        )
    
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
    
    def on_clear_completed_click(self):
        """Handler for 'Clear Completed' button click."""
        completed_orders = self.order_service.get_orders_by_status(OrderStatus.COMPLETED)
        cancelled_orders = self.order_service.get_orders_by_status(OrderStatus.CANCELLED)
        total = len(completed_orders) + len(cancelled_orders)
        
        if total == 0:
            messagebox.showinfo("Info", "No completed or cancelled orders to clear!")
            return
        
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Clear",
            f"Clear {total} completed/cancelled orders?\n\n"
            f"Completed: {len(completed_orders)}\n"
            f"Cancelled: {len(cancelled_orders)}\n\n"
            f"This action cannot be undone."
        )
        
        if confirm:
            count = self.order_service.clear_completed_orders()
            messagebox.showinfo(
                "Success",
                f"Cleared {count} orders successfully! 🗑️"
            )
    
    def show_context_menu(self, event):
        """Shows context menu on right-click."""
        # Select the item under cursor
        item = self.narudzbe_tree.identify_row(event.y)
        if item:
            self.narudzbe_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_cancel_order(self):
        """Handler for cancelling order from context menu."""
        selected = self.narudzbe_tree.selection()
        if not selected:
            return
        
        # Get order ID from selected row
        item = selected[0]
        values = self.narudzbe_tree.item(item, 'values')
        order_id = values[0]
        
        # Get order details
        order = self.order_service.get_order(order_id)
        if not order:
            messagebox.showerror("Error", "Order not found!")
            return
        
        # Check if order can be cancelled
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            messagebox.showwarning(
                "Cannot Cancel",
                f"Order is already {order.status.value}!"
            )
            return
        
        # Confirm cancellation
        confirm = messagebox.askyesno(
            "Confirm Cancellation",
            f"Cancel order {order_id}?\n\n"
            f"Beverage: {order.beverage_name}\n"
            f"Quantity: {order.quantity}\n"
            f"Status: {order.status.value}"
        )
        
        if confirm:
            # Cancel order asynchronously
            asyncio.run_coroutine_threadsafe(
                self.order_service.cancel_order(order_id),
                self.loop
            )
            messagebox.showinfo("Cancelled", f"Order {order_id} cancelled successfully! ❌")
    
    def update_gui(self):
        """Periodically updates the order display in the GUI."""
        # Clear current display
        for item in self.narudzbe_tree.get_children():
            self.narudzbe_tree.delete(item)
        
        # Status mapping (consistent with _update_order_in_tree)
        status_map = {
            OrderStatus.PENDING: "Sent",
            OrderStatus.PROCESSING: "Processing",
            OrderStatus.READY: "Ready",
            OrderStatus.COMPLETED: "Completed",
            OrderStatus.CANCELLED: "Cancelled"
        }
        
        # Add all orders
        all_orders = self.order_service.get_all_orders()
        for order in all_orders:
            time_str = order.created_at.strftime("%H:%M:%S")
            
            # Get display status text
            status_text = status_map.get(order.status, order.status.value)
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
        
        # Update status bar with active orders count
        if hasattr(self, 'status_label') and self.menu_from_api:
            active_orders = len([o for o in all_orders 
                                if o.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]])
            if active_orders > 0:
                self._update_status(
                    f"⚙️  Processing {active_orders} order(s) in parallel | "
                    f"Total: {len(all_orders)} | API: http://localhost:8080"
                )
            else:
                beverages = self.menu_from_api.get('beverages', [])
                available_count = len([b for b in beverages if b.get('available', True)])
                self._update_status(
                    f"✅ Ready | Menu: {available_count} beverages | "
                    f"Total orders: {len(all_orders)} | API: http://localhost:8080"
                )
        
        # Repeat every 500ms
        self.root.after(500, self.update_gui)
    
    def on_closing(self):
        """Handler for window closing."""
        # Cancel all pending tasks
        if self.loop and self.loop.is_running():
            # Cancel all tasks except the current one
            def cancel_all_tasks():
                tasks = asyncio.all_tasks(self.loop)
                for task in tasks:
                    if not task.done():
                        try:
                            task.cancel()
                        except Exception:
                            pass
                # Stop loop after short delay
                self.loop.call_later(0.1, self.loop.stop)
            
            self.loop.call_soon_threadsafe(cancel_all_tasks)
        
        # Close window after short delay
        self.root.after(200, self.root.destroy)


def main():
    try:
        root = tk.Tk()
        app = TabletGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\n\n👋 Application closed by user (Ctrl+C)")
        pass


if __name__ == "__main__":
    main()
