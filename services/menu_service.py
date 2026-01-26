"""
Async client for fetching menu from REST API.
Uses aiohttp for asynchronous HTTP requests.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
from decorators.logging_decorators import log_async_calls, catch_async_exceptions, performance_log_async


class MenuService:
    """Service for fetching beverage menu."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    @log_async_calls
    @performance_log_async
    @catch_async_exceptions(default_return=None)
    async def fetch_menu(self) -> Optional[Dict]:
        """
        Asynchronously fetches complete menu from API.
        
        Returns:
            Dictionary with menu or None if request failed
        """
        url = f"{self.base_url}/api/menu"
        
        try:
            # Use timeout to avoid hanging
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"Error: API returned status {response.status}")
                        return None
        except aiohttp.ClientError as e:
            print(f"Error connecting to API: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    @log_async_calls
    @catch_async_exceptions(default_return=None)
    async def fetch_beverage(self, beverage_id: int) -> Optional[Dict]:
        """
        Asynchronously fetches information about a single beverage.
        
        Args:
            beverage_id: Beverage ID
            
        Returns:
            Dictionary with beverage information or None
        """
        url = f"{self.base_url}/api/beverages/{beverage_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"Error: Beverage {beverage_id} not found")
                        return None
        except aiohttp.ClientError as e:
            print(f"Error connecting to API: {e}")
            return None
    
    async def get_available_beverages(self) -> List[Dict]:
        """
        Fetches only available beverages from menu.
        
        Returns:
            List of available beverages
        """
        menu = await self.fetch_menu()
        if menu and 'beverages' in menu:
            return [b for b in menu['beverages'] if b.get('available', True)]
        return []
    
    async def check_happy_hour(self) -> bool:
        """
        Checks if Happy Hour is active.
        
        Returns:
            True if Happy Hour is active, False otherwise
        """
        menu = await self.fetch_menu()
        if menu and 'happy_hour' in menu:
            return menu['happy_hour'].get('active', False)
        return False
    
    async def health_check(self) -> bool:
        """
        Checks if API is available.
        
        Returns:
            True if API is available, False otherwise
        """
        url = f"{self.base_url}/health"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return response.status == 200
        except:
            return False


# Demo functions

async def demo_fetch_menu():
    """Demo function that fetches menu."""
    print("=== Demo: Fetching menu ===\n")
    
    service = MenuService()
    
    # Check if server is available
    print("Checking API health...")
    is_healthy = await service.health_check()
    
    if not is_healthy:
        print("❌ API server is not running!")
        print("Please start the server first: python -m services.api_server")
        return
    
    print("✓ API server is running\n")
    
    # Fetch menu
    print("Fetching menu...")
    menu = await service.fetch_menu()
    
    if menu:
        print("\n📋 BEVERAGE MENU:")
        for beverage in menu['beverages']:
            status = "✓" if beverage['available'] else "✗"
            print(f"  {status} {beverage['name']}: {beverage['base_price']} {beverage['currency']}")
        
        print(f"\n🎉 Happy Hour: {'ACTIVE' if menu['happy_hour']['active'] else 'Inactive'}")
        if not menu['happy_hour']['active']:
            print(f"   Next Happy Hour: {menu['happy_hour']['start_time']} - {menu['happy_hour']['end_time']}")
            print(f"   Discount: {menu['happy_hour']['discount_percentage']}%")
    
    # Fetch individual beverage
    print("\n\nFetching individual beverage (Coffee, ID=1)...")
    coffee = await service.fetch_beverage(1)
    if coffee:
        print(f"✓ {coffee['name']}: {coffee['base_price']} {coffee['currency']}")
    
    # Fetch only available beverages
    print("\n\nFetching available beverages only...")
    available = await service.get_available_beverages()
    print(f"Found {len(available)} available beverages:")
    for b in available:
        print(f"  - {b['name']}")


def main():
    """Runs demo."""
    asyncio.run(demo_fetch_menu())


if __name__ == '__main__':
    main()
