"""Models package for data structures."""

# Import beverage classes to register them with Factory
from models.factory import BeverageFactory
from models.beverage import (
    Beverage,
    Coffee,
    Tea,
    Beer,
    Cappuccino,
    Espresso,
    Latte,
    Water,
    Juice,
    CocaCola,
    Wine
)

__all__ = [
    'BeverageFactory',
    'Beverage',
    'Coffee',
    'Tea',
    'Beer',
    'Cappuccino',
    'Espresso',
    'Latte',
    'Water',
    'Juice',
    'CocaCola',
    'Wine'
]
