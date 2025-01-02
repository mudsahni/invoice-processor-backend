from typing import Callable
from functools import wraps
from http import HTTPStatus
from flask import jsonify


def handle_exceptions(func: Callable) -> Callable:
    """Decorator to handle exceptions in controllers methods"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST
        except KeyError as e:
            return jsonify({'error': f'Missing required field: {str(e)}'}), HTTPStatus.BAD_REQUEST
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR
    return wrapper
