# Testing Documentation

## Overview
This application now has complete test coverage with **unit tests** and **doctest** examples.

## Running the Application

To start the tablet GUI:
```bash
python -m gui.tablet_gui
```

## Unit Tests (pytest)

### Running all tests:
```bash
pytest tests/ -v
```

### Running individual tests:
```bash
# Test pricing strategies
pytest tests/test_pricing_strategies.py -v

# Test beverage factory
pytest tests/test_beverage.py -v

# Test order service (async)
pytest tests/test_order_service.py -v
```

### Test coverage:

#### 1. **test_pricing_strategies.py**
- `TestStandardPricingStrategy` - Tests standard pricing
- `TestHappyHourStrategy` - Tests Happy Hour discounts (20% off)
- `TestBulkDiscountStrategy` - Tests bulk discounts (10% off for 5+)
- `TestStrategyIntegration` - Integration tests for all strategies

**What is tested:**
- Default and custom discount values
- Different quantities and prices
- Edge cases (0%, 100% discount)
- Strategy comparisons

#### 2. **test_beverage.py**
- `TestBeverage` - Tests basic Beverage class
- `TestBeverageFactory` - Tests Factory pattern
- `TestBeverageIntegration` - Integration tests

**What is tested:**
- Creating beverages through factory
- Applying pricing strategies to beverages
- Changing strategies for the same beverage
- All available beverages (Coffee, Tea, Beer, etc.)

#### 3. **test_order_service.py**
- `TestOrder` - Tests Order model
- `TestOrderService` - Tests asynchronous order processing
- `TestOrderIntegration` - Integration and performance tests

**What is tested:**
- Creating orders
- Status transitions (PENDING → PROCESSING → READY → COMPLETED)
- Parallel processing of multiple orders (`asyncio`)
- Performance (verifying orders don't block each other)
- Independence between different OrderService instances

### Async tests
Tests use `@pytest.mark.asyncio` to test asynchronous functions:
```python
@pytest.mark.asyncio
async def test_parallel_order_processing(self, order_service):
    # Test paralelne obrade
    tasks = [
        order_service.create_order("Coffee", 1, 2.5, 0.1),
        order_service.create_order("Tea", 1, 2.0, 0.1)
    ]
    orders = await asyncio.gather(*tasks)
```

---

## Doctest

### Running doctests:
```bash
# Running doctest for pricing strategies
python services/pricing_strategy.py

# Or via doctest module
python -m doctest services/pricing_strategy.py -v
```

### Doctest examples in code:

#### StandardPricingStrategy
```python
>>> strategy = StandardPricingStrategy()
>>> strategy.calculate_price(10.0)
10.0
>>> strategy.calculate_price(5.5)
5.5
```

#### HappyHourStrategy
```python
>>> strategy = HappyHourStrategy(discount_percentage=20.0)
>>> strategy.calculate_price(10.0)
8.0
>>> strategy = HappyHourStrategy(discount_percentage=50.0)
>>> strategy.calculate_price(10.0)
5.0
```

#### BulkDiscountStrategy
```python
>>> strategy = BulkDiscountStrategy(min_quantity=5, discount_percentage=10.0)
>>> strategy.calculate_price(10.0, quantity=3)
10.0
>>> strategy.calculate_price(10.0, quantity=5)
9.0
```

---

## Implemented Functionalities

### 1. HappyHourStrategy - USED
- **Where:** GUI checkbox "Happy Hour (20% off)"
- **How:** When checkbox is checked, 20% discount is applied to price
- **Tests:** `test_pricing_strategies.py::TestHappyHourStrategy`

### 2. BulkDiscountStrategy - USED
- **Where:** Automatically applied for orders >= 5 items
- **How:** When quantity >= 5, 10% discount is automatically applied
- **Tests:** `test_pricing_strategies.py::TestBulkDiscountStrategy`

### 3. Unit tests
- **Where:** `tests/` folder
- **Number of tests:** 30+ tests
- **Coverage:** Pricing strategies, Beverage factory, Order service

### 4. Doctest
- **Where:** `services/pricing_strategy.py`
- **Number of examples:** 15+ doctest examples
- **Running:** `python services/pricing_strategy.py`

---

## Testing in Practice

### Scenario 1: Happy Hour discount
1. Start GUI: `python gui/tablet_gui.py`
2. Select beverage (e.g., Coffee 2.5 EUR)
3. Check "Happy Hour (20% off)"
4. Click "Place Order"
5. **Result:** In terminal: `Happy Hour applied: 2.50 EUR -> 2.00 EUR (-20%)`

### Scenario 2: Bulk discount
1. Start GUI
2. Select beverage (e.g., Beer 3.5 EUR)
3. Enter quantity: **5**
4. Click "Place Order"
5. **Result:** `Bulk Discount applied: 17.50 EUR -> 15.75 EUR (-10% for 5 items)`

### Scenario 3: Parallel processing
1. Start 4 GUI instances: `python test_parallel_orders.py`
2. Create orders on all GUIs at once
3. **Result:** All orders are processed simultaneously (async)

---

## Installing pytest (if not installed)

```bash
pip install pytest pytest-asyncio
```

or

```bash
conda install pytest pytest-asyncio
```

---

## CI/CD Integration
Tests are ready for CI/CD pipelines:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
      - name: Run doctests
        run: python -m doctest services/pricing_strategy.py
```

---

## Summary

**HappyHourStrategy** - Implemented and used in GUI  
**BulkDiscountStrategy** - Implemented and automatically applied  
**Unit tests** - 30+ tests, cover all key functionalities  
**Doctest** - 15+ examples in code with documentation  
**Async tests** - Testing parallel order processing  
**Integration tests** - Testing complete workflow  

**You can now:**
- Run `pytest tests/ -v` and see all tests
- Run `python services/pricing_strategy.py` and see doctests
- Run GUI and see Happy Hour checkbox in action
- Order 5+ items and see bulk discount
