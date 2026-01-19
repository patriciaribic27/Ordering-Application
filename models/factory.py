from typing import Dict, Type
from abc import ABCMeta
from decorators.logging_decorators import log_calls, catch_exceptions


class BeverageRegistryMeta(ABCMeta):
    """Metaclass that automatically registers all beverage classes in the factory."""
    
    _registry: Dict[str, Type] = {}
    
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Don't register abstract base classes
        if name != 'Beverage' and not attrs.get('__abstractmethods__'):
            # Register class under its name
            mcs._registry[name] = cls
            
            # Add lowercase alias for easier access
            mcs._registry[name.lower()] = cls
        
        return cls


class BeverageFactory:
    """Factory for creating beverages based on string."""
    
    @staticmethod
    @log_calls
    @catch_exceptions(default_return=None, log_traceback=False)
    def create(beverage_type: str):
        """
        Creates a beverage instance based on name.
        
        Args:
            beverage_type: Beverage name (e.g. "Coffee", "coffee", "Tea", etc.)
            
        Returns:
            Instance of the corresponding beverage class
            
        Raises:
            ValueError: If beverage is not registered
        """
        beverage_class = BeverageRegistryMeta._registry.get(beverage_type)
        
        if beverage_class is None:
            available = [k for k in BeverageRegistryMeta._registry.keys() 
                        if not k[0].islower()]
            raise ValueError(
                f"Unknown beverage: {beverage_type}. "
                f"Available beverages: {', '.join(available)}"
            )
        
        return beverage_class()
    
    @staticmethod
    def get_available_beverages():
        """Returns list of all available beverages (only capitalized names)."""
        return [name for name in BeverageRegistryMeta._registry.keys() 
                if name[0].isupper()]
