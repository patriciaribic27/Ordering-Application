# Demo Scripts

This folder contains demonstration scripts that showcase the application's features.

## Available Demos:

### 1. `demo_complete.py`
Complete demonstration of automatic strategy switching based on time.
- Shows Happy Hour pricing (16:00-18:00)
- Standard pricing for regular hours
- Bulk discount for large orders
- Uses mock time to demonstrate all scenarios

**Run:**
```bash
python demos/demo_complete.py
```

### 2. `demo_strategy_pattern.py`
Educational demonstration of the Strategy Pattern implementation.
- Shows how to manually switch between pricing strategies
- Demonstrates proper Strategy Pattern usage
- Compares different pricing strategies side-by-side

**Run:**
```bash
python demos/demo_strategy_pattern.py
```

### 3. `demo_parallel_orders.py`
Interactive demo for testing parallel order processing.
- Launches multiple tablet GUI instances
- Demonstrates asynchronous menu fetching
- Shows parallel processing of simultaneous orders

**Run:**
```bash
python demos/demo_parallel_orders.py
```

## Purpose

These demos are designed to:
- Showcase application features to stakeholders
- Provide examples for developers
- Test system behavior in various scenarios
- Demonstrate design patterns in action
