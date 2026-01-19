"""
Decorators for logging and exception handling.
All logs are written to log.txt.
"""

import functools
import asyncio
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable, Any


# Path to log file
LOG_FILE = Path(__file__).parent.parent / "log.txt"


def log_to_file(message: str):
    """Helper function for writing to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message)


def log_calls(func: Callable) -> Callable:
    """
    Decorator for logging function calls.
    Records function name, arguments and return value.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        
        # Format arguments for log
        args_str = ", ".join([repr(a) for a in args[:3]])  # First 3 arguments
        if len(args) > 3:
            args_str += ", ..."
        
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in list(kwargs.items())[:3]])
        if len(kwargs) > 3:
            kwargs_str += ", ..."
        
        params = ", ".join(filter(None, [args_str, kwargs_str]))
        
        log_to_file(f"CALL: {func_name}({params})")
        
        try:
            result = func(*args, **kwargs)
            log_to_file(f"RETURN: {func_name} -> {type(result).__name__}")
            return result
        except Exception as e:
            log_to_file(f"ERROR in {func_name}: {type(e).__name__}: {str(e)}")
            raise
    
    return wrapper


def log_async_calls(func: Callable) -> Callable:
    """
    Decorator for logging async functions.
    Same as log_calls, but for async/await functions.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        
        # Format arguments
        args_str = ", ".join([repr(a) for a in args[:3]])
        if len(args) > 3:
            args_str += ", ..."
        
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in list(kwargs.items())[:3]])
        if len(kwargs) > 3:
            kwargs_str += ", ..."
        
        params = ", ".join(filter(None, [args_str, kwargs_str]))
        
        log_to_file(f"ASYNC CALL: {func_name}({params})")
        
        try:
            result = await func(*args, **kwargs)
            log_to_file(f"ASYNC RETURN: {func_name} -> {type(result).__name__}")
            return result
        except Exception as e:
            log_to_file(f"ASYNC ERROR in {func_name}: {type(e).__name__}: {str(e)}")
            raise
    
    return wrapper


def catch_exceptions(default_return=None, log_traceback=True):
    """
    Decorator for catching and logging exceptions.
    
    Args:
        default_return: Value to return if exception occurs
        log_traceback: If True, logs full traceback
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"EXCEPTION in {func_name}: {type(e).__name__}: {str(e)}"
                log_to_file(error_msg)
                
                if log_traceback:
                    tb = traceback.format_exc()
                    log_to_file(f"TRACEBACK:\n{tb}")
                
                return default_return
        
        return wrapper
    
    return decorator


def catch_async_exceptions(default_return=None, log_traceback=True):
    """
    Decorator for catching exceptions in async functions.
    
    Args:
        default_return: Value to return if exception occurs
        log_traceback: If True, logs full traceback
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_msg = f"ASYNC EXCEPTION in {func_name}: {type(e).__name__}: {str(e)}"
                log_to_file(error_msg)
                
                if log_traceback:
                    tb = traceback.format_exc()
                    log_to_file(f"TRACEBACK:\n{tb}")
                
                return default_return
        
        return wrapper
    
    return decorator


def performance_log(func: Callable) -> Callable:
    """
    Decorator that measures and logs function execution time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            log_to_file(f"PERFORMANCE: {func_name} executed in {duration:.4f}s")
            return result
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            log_to_file(f"PERFORMANCE: {func_name} failed after {duration:.4f}s")
            raise
    
    return wrapper


def performance_log_async(func: Callable) -> Callable:
    """
    Decorator that measures and logs async function execution time.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = datetime.now()
        
        try:
            result = await func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            log_to_file(f"ASYNC PERFORMANCE: {func_name} executed in {duration:.4f}s")
            return result
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            log_to_file(f"ASYNC PERFORMANCE: {func_name} failed after {duration:.4f}s")
            raise
    
    return wrapper


# Demo functions

@log_calls
def sample_function(x: int, y: int) -> int:
    """Demo function with logging."""
    return x + y


@catch_exceptions(default_return=0)
def sample_with_error(x: int) -> int:
    """Demo function that throws exception."""
    if x < 0:
        raise ValueError("x must be a positive number")
    return x * 2


@log_async_calls
@performance_log_async
async def sample_async_function(delay: float) -> str:
    """Demo async function."""
    await asyncio.sleep(delay)
    return f"Finished after {delay}s"


async def demo():
    """Demo function for testing decorators."""
    print("=== Demo: Decorators ===\n")
    print(f"Log file: {LOG_FILE}\n")
    
    # Test logging
    print("1. Testing log_calls:")
    result = sample_function(5, 3)
    print(f"   Result: {result}\n")
    
    # Test exception catching
    print("2. Testing catch_exceptions:")
    result1 = sample_with_error(10)
    print(f"   Valid input result: {result1}")
    result2 = sample_with_error(-5)
    print(f"   Invalid input result: {result2} (exception caught)\n")
    
    # Test async
    print("3. Testing async decorators:")
    result = await sample_async_function(0.5)
    print(f"   Result: {result}\n")
    
    print(f"\n✓ Check {LOG_FILE} for detailed logs")


def main():
    """Runs demo."""
    # Clear old log
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    
    log_to_file("=" * 50)
    log_to_file("NEW SESSION STARTED")
    log_to_file("=" * 50)
    
    asyncio.run(demo())


if __name__ == '__main__':
    main()
