# Café Ordering Application

A Python application that simulates self-service drink ordering in a café using tablet-based interfaces.

Each table in the café has a tablet where guests can independently place drink orders through a graphical user interface (GUI), without interacting with a waiter.

---

## Features

- Tablet-based GUI built with **Tkinter**
- Asynchronous order processing using **asyncio**
- REST API integration for fetching drink prices (**aiohttp**)
- Parallel handling of multiple orders and tables
- Dynamic pricing using the **Strategy pattern**:
  - Standard pricing
  - Happy Hour discounts
  - Bulk order discounts
- Beverage creation using the **Factory pattern**
- CSV and PDF export of daily order reports
- Full test coverage with **pytest** and **doctest**
- Logging and exception handling using decorators

- ---

## Installation

Install project dependencies using:

```bash
pip install -r requirements.txt

# How It Works

The application represents a café environment where each table is equipped with a tablet.
Guests can browse available drinks, select quantities, and place orders independently through the GUI.

Once an order is placed:
- The order is sent asynchronously for processing
- Multiple orders can be handled in parallel
- Order status is updated in real time (e.g. sent, processing, ready)

Drink prices are fetched asynchronously from a REST API, ensuring that the GUI remains responsive even when multiple tables are active at the same time.

---

## Pricing Logic

The application uses the Strategy design pattern to calculate drink prices dynamically.

Available pricing strategies include:
- **Standard pricing** – default price without discounts
- **Happy Hour pricing** – percentage-based discount applied during a defined time window
- **Bulk discount pricing** – automatic discount applied when ordering a larger quantity of the same drink

The pricing strategy is selected automatically based on application logic and order context.

---

## Concurrency and Asynchronous Processing

Asynchronous programming is implemented using `asyncio` and `aiohttp`.

This allows the application to:
- Fetch drink menus from a REST API without blocking the GUI
- Process multiple orders concurrently
- Simulate multiple tables placing orders at the same time

Each order is processed independently to ensure realistic parallel behavior.

---

## Logging and Error Handling

Function calls and asynchronous operations are logged using custom decorators.
All important actions and errors are written to log files, making the application easier to debug and monitor during execution.

---

## Reports

At the end of the day, order data can be exported into:
- **CSV format** for data analysis
- **PDF format** for reporting and record keeping

These reports summarize all processed orders for the selected period.











