import json
from datetime import datetime
import os
from typing import Dict, Any
import requests

# Get environment variables (for demo purposes)
API_KEY = os.environ.get('FRED_API_KEY', 'demo-key')
INFLATION_DATA_SOURCE = "https://api.stlouisfed.org/fred/series/observations"

# ensure a data is in the YYYY-MM-DD format, checks that the date isn't in the future
def is_this_a_valid_date(date_str):
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        # Get the current date (without time)
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if the date is not in the future
        return parsed_date <= current_date
    except ValueError:
        return False

def handler(event, context):

    path = event.get('path', '')
        
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

    query_params = event.get('queryStringParameters', {}) or {}
    
    try:
        amount = float(query_params.get('amount'))
        
        start_date = query_params.get('start_date')
        end_date= query_params.get('end_date')
        
        if start_date and end_date and amount:

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
            start_date_from_fred = observations[0]['date']
            end_cpi = float(observations[-1]['value'])
            end_date_from_fred = observations[-1]['date']
           
            
            if reverse:
                adjusted_amount = amount * (start_cpi / end_cpi)
            else:
                adjusted_amount = amount * (end_cpi / start_cpi)
            
            data_to_return = {
                'start_date': start_date_from_fred,
                'end_date': end_date_from_fred,
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

# Create standardized API response in the format specific for lambdas 
def response(status_code: int, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Enable CORS
        },
        'body': json.dumps(data)
    }