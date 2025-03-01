import json
from datetime import datetime
import os
from typing import Dict, Any
import requests

# Get environment variables (for demo purposes)
API_KEY = os.environ.get('FRED_API_KEY', 'demo-key')
INFLATION_DATA_SOURCE = "https://api.stlouisfed.org/fred/series/observations"

# ensure a data is in the YYYY-MM-DD format
def is_this_a_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

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
        return calc_inflation(event, True)
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

def get_cpi_data(start_date, end_date):
        print(f"\n\n {start_date} \n {end_date}")
        params = {
            'series_id': 'CPIAUCSL',  # CPI for All Urban Consumers: All Items
            'api_key': API_KEY,
            'file_type': 'json',
            'observation_start': start_date,
            'observation_end': end_date
        }
        
        response = requests.get(INFLATION_DATA_SOURCE, params=params)
        if response.status_code != 200:
            raise Exception(f"FRED API request failed: {response.text}")
            
        return response.json()

def calc_inflation(event, reverse = False):

    # Extract query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    
    try:
        # Get the amount parameter with default value of 100
        amount = float(query_params.get('amount', 100))
        
        # Check if date parameters are provided
        start_date = query_params.get('start_date')
        end_date= query_params.get('end_date')
        
        if start_date and end_date and amount:
            # Parse dates
            if not is_this_a_valid_date(start_date) or not is_this_a_valid_date(end_date):
                return response(400, {
                    "message": "Invalid parameter format. Please check your input values.",
                    "error": "Dates must me in the YYYY-MM-DD format"
                })
            
            data = get_cpi_data(start_date, end_date)
            observations = data['observations']
            
            if not observations:
                raise Exception("No CPI data found for the given date range")
                
            start_cpi = float(observations[0]['value'])
            end_cpi = float(observations[-1]['value'])
            
            if reverse:
                adjusted_amount = amount * (start_cpi / end_cpi)
            else:
                adjusted_amount = amount * (end_cpi / start_cpi)
            
            data_to_return = {
                'start_date': start_date,
                'end_date': end_date,
                'original_amount': amount,
                'adjusted_amount': round(adjusted_amount, 2),
            }
            
            return response(200, data_to_return)
        else:
            return response(400, {
                "message": "Invalid parameter format. Please check your input values.",
            })
            
    except ValueError as e:
        return response(400, {
            "message": "Invalid parameter format. Please check your input values.",
            "error": str(e)
        })
    except Exception as e:
        return response(500, {
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
        },
        'body': json.dumps(data)
    }