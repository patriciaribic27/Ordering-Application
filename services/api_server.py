"""
Mock REST API server for beverage menu.
Uses aiohttp for async web server.
"""

from aiohttp import web
import json


async def get_menu(request):
    """Endpoint that returns beverage menu in JSON format."""
    menu = {
        "beverages": [
            {
                "id": 1,
                "name": "Espresso",
                "base_price": 2.00,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 2,
                "name": "Coffee",
                "base_price": 2.50,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 3,
                "name": "Cappuccino",
                "base_price": 3.00,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 4,
                "name": "Latte",
                "base_price": 3.50,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 5,
                "name": "Tea",
                "base_price": 2.00,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 6,
                "name": "Beer",
                "base_price": 3.50,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 7,
                "name": "Wine",
                "base_price": 4.50,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 8,
                "name": "CocaCola",
                "base_price": 2.50,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 9,
                "name": "Juice",
                "base_price": 2.80,
                "currency": "EUR",
                "available": True
            },
            {
                "id": 10,
                "name": "Water",
                "base_price": 1.00,
                "currency": "EUR",
                "available": True
            }
        ],
        "happy_hour": {
            "active": False,
            "discount_percentage": 20.0,
            "start_time": "17:00",
            "end_time": "19:00"
        }
    }
    return web.json_response(menu)


async def get_beverage(request):
    """Endpoint that returns information about a single beverage."""
    beverage_id = int(request.match_info['id'])
    
    beverages = {
        1: {"id": 1, "name": "Coffee", "base_price": 2.50, "currency": "EUR"},
        2: {"id": 2, "name": "Tea", "base_price": 2.00, "currency": "EUR"},
        3: {"id": 3, "name": "Beer", "base_price": 3.50, "currency": "EUR"},
    }
    
    if beverage_id in beverages:
        return web.json_response(beverages[beverage_id])
    else:
        return web.json_response(
            {"error": f"Beverage with id {beverage_id} not found"},
            status=404
        )


async def health_check(request):
    """Health check endpoint."""
    return web.json_response({"status": "ok", "service": "beverage-api"})


def create_app():
    """Creates aiohttp application with routes."""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/api/menu', get_menu)
    app.router.add_get('/api/beverages/{id}', get_beverage)
    app.router.add_get('/health', health_check)
    
    return app


def main():
    """Starts server."""
    app = create_app()
    print("Starting mock REST API server...")
    print("Available endpoints:")
    print("  - GET http://localhost:8080/api/menu")
    print("  - GET http://localhost:8080/api/beverages/{id}")
    print("  - GET http://localhost:8080/health")
    print("\nServer running on http://localhost:8080")
    print("Press Ctrl+C to stop")
    
    web.run_app(app, host='localhost', port=8080)


if __name__ == '__main__':
    main()
