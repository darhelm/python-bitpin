"""# Utility functions for bitpin module."""

import asyncio
import inspect
import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any


def get_loop() -> asyncio.AbstractEventLoop:
    """
    Get event loop.

    Returns:
        asyncio.AbstractEventLoop
    """

    try:
        loop = asyncio.get_event_loop()
        return loop
    except RuntimeError as e:
        if str(e).startswith("There is no current event loop in thread"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

        raise e


def validate_parameters(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that validates function parameters against its signature.
    Issues a warning for any invalid parameters and suggests using the deprecated module.

    Args:
        func (Callable[..., Any]): The function to be decorated.

    Returns:
        Callable[..., Any]: The decorated function which validates parameters.
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        return await _validate_and_call(func, args, kwargs)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        return asyncio.run(_validate_and_call(func, args, kwargs))

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper


async def _validate_and_call(
    func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict
) -> Any:
    signature = inspect.signature(func)
    valid_params = set(signature.parameters.keys())

    for param in kwargs:
        if param not in valid_params:
            warnings.warn(
                f"Warning: '{param}' is not a valid parameter for '{func.__name__}'. "
                f"Valid parameters are: {', '.join(valid_params)}. "
                "If you intended to use the deprecated version, please import from 'bitpin.deprecated'.",
                DeprecationWarning,
                stacklevel=2,
            )

    for idx in range(len(args)):
        param_name = list(valid_params)[idx] if idx < len(valid_params) else None
        if param_name and param_name not in valid_params:
            warnings.warn(
                f"Warning: Argument at position {idx} is not a valid parameter for '{func.__name__}'. "
                f"Valid parameters are: {', '.join(valid_params)}. "
                "If you intended to use the deprecated version, please import desired client from 'bitpin.deprecated'.",
                UserWarning,
                stacklevel=2,
            )

    try:
        return (
            await func(*args, **kwargs)
            if inspect.iscoroutinefunction(func)
            else func(*args, **kwargs)
        )
    except TypeError as e:
        msg = (
            f"Error: {e!s}. This may be due to unexpected keyword arguments. "
            f"Valid parameters are: {', '.join(valid_params)}. "
            "If you intended to use the deprecated version, please import desired client from 'bitpin.deprecated'."
        )
        raise TypeError(
            msg,
        ) from e

    except NameError as e:
        msg = (
            f"Error: {e!s}. This indicates that a variable name is not defined."
            f"Valid parameters are: {', '.join(valid_params)}. "
            "If you intended to use the deprecated version, please import desired client from 'bitpin.deprecated'."
        )
        raise NameError(
            msg,
        ) from e
