import json
import datetime
import os
from typing import Dict, Any, Tuple, Optional

# Get environment variables (for demo purposes)
API_KEY = os.environ.get('API_KEY', 'demo-key')
INFLATION_DATA_SOURCE = os.environ.get('INFLATION_DATA_SOURCE', 'example-source')

def handler(event, context):
    # Extract HTTP method
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    
    # For debugging
    print(f"Request path: {path}, method: {http_method}")
    print(f"Event: {json.dumps(event)}")
    
    # Route based on path and method
    if path == "/inflation/calc":
        if http_method == "GET":
            return calc_inflation_get(event)
        elif http_method == "POST":
            return calc_inflation_post(event)
        else:
            return method_not_allowed(["GET", "POST"])
    elif path == "/inflation/reverse":
        if http_method == "GET":
            return reverse_inflation_get(event)
        elif http_method == "POST":
            return reverse_inflation_post(event)
        else:
            return method_not_allowed(["GET", "POST"])
    elif path == "/inflation":
        return handle_base_inflation(event)
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Not Found',
                'path': path
            })
        }

def handle_base_inflation(event):
    data = {
        "message": "Welcome to the inflation API",
        "available_endpoints": [
            "/inflation/calc",
            "/inflation/reverse"
        ]
    }
    return response(200, data)

def calc_inflation_get(event):
    # Extract query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    amount = float(query_params.get('amount', 100))
    years = int(query_params.get('years', 5))
    rate = float(query_params.get('rate', 2.5))
    
    # Calculate inflation
    future_value = amount * (1 + rate/100) ** years
    
    data = {
        "message": "Inflation calculation result (GET)",
        "input": {
            "amount": amount,
            "years": years,
            "annual_rate": rate
        },
        "future_value": round(future_value, 2)
    }
    
    return response(200, data)

def calc_inflation_post(event):
    # Parse JSON body
    body = parse_body(event)
    if body is None:
        return response(400, {"message": "Invalid JSON in request body"})
    
    # Extract parameters from body
    amount = float(body.get('amount', 100))
    
    # Handle date-based calculation
    start_date_str = body.get('start_date')
    end_date_str = body.get('end_date')
    
    try:
        if start_date_str and end_date_str:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            
            # Calculate years difference
            years_diff = (end_date - start_date).days / 365.25
            
            # For demo, using a fixed rate, but you would likely look up
            # actual inflation rates for these time periods from an API or database
            rate = 2.5  # Example fixed annual rate
            
            future_value = amount * (1 + rate/100) ** years_diff
            
            data = {
                "message": "Inflation calculation result (POST)",
                "input": {
                    "amount": amount,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "years_difference": round(years_diff, 2),
                    "annual_rate": rate
                },
                "future_value": round(future_value, 2),
                "data_source": INFLATION_DATA_SOURCE
            }
            
            return response(200, data)
        else:
            # Fall back to simpler calculation if dates not provided
            rate = float(body.get('rate', 2.5))
            years = float(body.get('years', 5))
            
            future_value = amount * (1 + rate/100) ** years
            
            data = {
                "message": "Inflation calculation result (POST)",
                "input": {
                    "amount": amount,
                    "years": years,
                    "annual_rate": rate
                },
                "future_value": round(future_value, 2)
            }
            
            return response(200, data)
            
    except ValueError as e:
        return response(400, {
            "message": "Invalid date format. Please use YYYY-MM-DD format.",
            "error": str(e)
        })

def reverse_inflation_post(event):
    # Parse JSON body
    body = parse_body(event)
    if body is None:
        return response(400, {"message": "Invalid JSON in request body"})
    
    # Extract parameters from body
    current_amount = float(body.get('amount', 100))
    
    # Handle date-based calculation
    start_date_str = body.get('start_date')
    end_date_str = body.get('end_date')
    
    try:
        if start_date_str and end_date_str:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            
            # Calculate years difference
            years_diff = (end_date - start_date).days / 365.25
            
            # For demo, using a fixed rate
            rate = 2.5  # Example fixed annual rate
            
            # Reverse calculation (what past amount would equal current_amount today)
            past_value = current_amount / ((1 + rate/100) ** years_diff)
            
            data = {
                "message": "Reverse inflation calculation result (POST)",
                "input": {
                    "current_amount": current_amount,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "years_difference": round(years_diff, 2),
                    "annual_rate": rate
                },
                "past_value": round(past_value, 2),
                "data_source": INFLATION_DATA_SOURCE
            }
            
            return response(200, data)
        else:
            # Fall back to simpler calculation if dates not provided
            rate = float(body.get('rate', 2.5))
            years = float(body.get('years', 5))
            
            past_value = current_amount / ((1 + rate/100) ** years)
            
            data = {
                "message": "Reverse inflation calculation result (POST)",
                "input": {
                    "current_amount": current_amount,
                    "years": years,
                    "annual_rate": rate
                },
                "past_value": round(past_value, 2)
            }
            
            return response(200, data)
            
    except ValueError as e:
        return response(400, {
            "message": "Invalid date format. Please use YYYY-MM-DD format.",
            "error": str(e)
        })

def reverse_inflation_get(event):
    # Extract query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    current_amount = float(query_params.get('amount', 100))
    years = int(query_params.get('years', 5))
    rate = float(query_params.get('rate', 2.5))
    
    # Reverse calculation
    past_value = current_amount / ((1 + rate/100) ** years)
    
    data = {
        "message": "Reverse inflation calculation result (GET)",
        "input": {
            "current_amount": current_amount,
            "years_ago": years,
            "annual_rate": rate
        },
        "past_value": round(past_value, 2)
    }
    
    return response(200, data)

def method_not_allowed(allowed_methods):
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Allow': ', '.join(allowed_methods)
        },
        'body': json.dumps({
            'message': 'Method Not Allowed',
            'allowed_methods': allowed_methods
        })
    }

def parse_body(event) -> Optional[Dict[str, Any]]:
    """Parse JSON body from request event"""
    try:
        if 'body' in event and event['body']:
            return json.loads(event['body'])
        return {}
    except json.JSONDecodeError:
        return None

def response(status_code: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Enable CORS
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
        },
        'body': json.dumps(data)
    }