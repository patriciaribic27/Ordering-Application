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











