import json
import datetime
import os
from typing import Dict, Any

# Get environment variables (for demo purposes)
API_KEY = os.environ.get('API_KEY', 'demo-key')
INFLATION_DATA_SOURCE = os.environ.get('INFLATION_DATA_SOURCE', 'example-source')

def handler(event, context):
    # Extract HTTP method and path
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    
    # For debugging
    print(f"Request path: {path}, method: {http_method}")
    print(f"Event: {json.dumps(event)}")
    
    # Route based on path
    if path == "/inflation/calc":
        return calc_inflation(event)
    elif path == "/inflation/reverse":
        return reverse_inflation(event)
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
            "/inflation/calc?amount=1000&start_date=2020-01-01&end_date=2025-01-01",
            "/inflation/reverse?amount=1000&start_date=2020-01-01&end_date=2025-01-01"
        ]
    }
    return response(200, data)

def calc_inflation(event):
    # Extract query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    
    try:
        # Get the amount parameter with default value of 100
        amount = float(query_params.get('amount', 100))
        
        # Check if date parameters are provided
        start_date_str = query_params.get('start_date')
        end_date_str = query_params.get('end_date')
        
        if start_date_str and end_date_str:
            # Parse dates
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            
            # Calculate years difference
            years_diff = (end_date - start_date).days / 365.25
            
            # For demo, using a fixed rate, but you would likely look up
            # actual inflation rates for these time periods from an API or database
            rate = float(query_params.get('rate', 2.5))  # Default 2.5% if not specified
            
            future_value = amount * (1 + rate/100) ** years_diff
            
            data = {
                "message": "Inflation calculation result",
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
            rate = float(query_params.get('rate', 2.5))
            years = float(query_params.get('years', 5))
            
            future_value = amount * (1 + rate/100) ** years
            
            data = {
                "message": "Inflation calculation result",
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
            "message": "Invalid parameter format. Please check your input values.",
            "error": str(e)
        })

def reverse_inflation(event):
    # Extract query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    
    try:
        # Get the amount parameter with default value of 100
        current_amount = float(query_params.get('amount', 100))
        
        # Check if date parameters are provided
        start_date_str = query_params.get('start_date')
        end_date_str = query_params.get('end_date')
        
        if start_date_str and end_date_str:
            # Parse dates
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            
            # Calculate years difference
            years_diff = (end_date - start_date).days / 365.25
            
            # For demo, using a fixed rate
            rate = float(query_params.get('rate', 2.5))  # Default 2.5% if not specified
            
            # Reverse calculation (what past amount would equal current_amount today)
            past_value = current_amount / ((1 + rate/100) ** years_diff)
            
            data = {
                "message": "Reverse inflation calculation result",
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
            rate = float(query_params.get('rate', 2.5))
            years = float(query_params.get('years', 5))
            
            past_value = current_amount / ((1 + rate/100) ** years)
            
            data = {
                "message": "Reverse inflation calculation result",
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
            "message": "Invalid parameter format. Please check your input values.",
            "error": str(e)
        })

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