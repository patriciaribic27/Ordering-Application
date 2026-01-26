# Cafe Ordering Application

Python application that simulates self-service beverage ordering in a cafe via tablet.

## Description

Each table in the cafe has a tablet where guests can independently order beverages through a graphical user interface without waiter assistance. The application supports parallel processing of multiple orders, simulating multiple tables ordering simultaneously.

## Features

- Graphical user interface built with Tkinter library
- Left side: beverage selection, quantity input, order confirmation
- Right side: tabular display of orders with status
- Parallel order processing using asyncio
- Asynchronous menu fetching via REST API (aiohttp)
- Factory pattern for creating beverage objects
- Strategy pattern for price calculation (standard price, discount, happy hour)
- Decorators for logging function calls and exception handling
- Daily report export in CSV and PDF format
- Unit tests for key components

## Requirements

- Python 3.8 or higher
- Packages listed in requirements.txt

## Installation

```bash
pip install -r requirements.txt
```

## Running

Start the main application:

```bash
python main.py
```

Start GUI directly:

```bash
python -m gui.tablet_gui
```

Test parallel processing with multiple instances:

```bash
python test_parallel_orders.py
```

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run individual tests:

```bash
pytest tests/test_pricing_strategies.py -v
pytest tests/test_order_service.py -v
pytest tests/test_beverage.py -v
```

## Architecture

### Design Patterns

**Factory Pattern** - Creating beverage objects
- `models/factory.py` - BeverageFactory with metaclass registration
- `models/beverage.py` - Beverage classes (Coffee, Tea, Beer, etc.)

**Strategy Pattern** - Price calculation
- `services/pricing_strategy.py` - PricingContext and strategies
- StandardPricingStrategy - standard price
- HappyHourStrategy - discount (16:00-18:00)
- BulkDiscountStrategy - discount for larger quantities

### Decorators

- `@log_calls` - logging function calls
- `@log_async_calls` - logging asynchronous functions
- `@catch_exceptions` - catching and logging exceptions
- `@catch_async_exceptions` - catching exceptions in async functions
- `@performance_log` - performance measurement

All logs are saved to `log.txt`.

### Concurrency

- `asyncio` - parallel order processing
- `aiohttp` - REST API server and client
- `OrderService` - asynchronous order processing with status changes
- Event loop in separate thread for GUI integration

### Project Structure

```
aplikacija za narucivanje/
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
├── log.txt                 # Log file
├── decorators/
│   └── logging_decorators.py
├── models/
│   ├── beverage.py        # Beverage classes
│   └── factory.py         # Factory pattern
├── services/
│   ├── api_server.py      # REST API server
│   ├── menu_service.py    # API client
│   ├── order_service.py   # Order processing
│   └── pricing_strategy.py
├── gui/
│   └── tablet_gui.py      # Tkinter GUI
├── exporters/
│   ├── csv_exporter.py
│   └── pdf_exporter.py
├── tests/
│   ├── test_beverage.py
│   ├── test_order_service.py
│   └── test_pricing_strategies.py
├── izvjestaji/            # Report exports
└── reports/               # Report exports
```

## Technologies

- Python 3.8+
- Tkinter (GUI)
- asyncio (concurrency)
- aiohttp (REST API)
- pytest (testing)
- reportlab (PDF reports)
- csv (CSV reports)

## REST API

Server automatically starts on `http://localhost:8080`

Endpoints:
- `GET /api/menu` - complete menu
- `GET /api/beverages/{id}` - individual beverage
- `GET /health` - server status

## Reports

Reports are generated in `izvjestaji/` and `reports/` directories:
- CSV format with order details and statistics
- PDF format with formatted reports and tables




