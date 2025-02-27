import requests
from datetime import datetime

class FREDInflationCalculator:
    def __init__(self, api_key):
        """
        Initialize the calculator with your FRED API key.
        Get one at: https://fred.stlouisfed.org/docs/api/api_key.html
        """
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        
    def get_cpi_data(self, start_date, end_date):
        """
        Fetch CPI data from FRED for the given date range.
        Uses CPIAUCSL series (Consumer Price Index for All Urban Consumers: All Items)
        """
        params = {
            'series_id': 'CPIAUCSL',  # CPI for All Urban Consumers: All Items
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': start_date,
            'observation_end': end_date
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"FRED API request failed: {response.text}")
            
        return response.json()
    
    def calculate_inflation(self, start_date, end_date):
        """
        Calculate inflation between two dates.
        Dates should be in 'YYYY-MM-DD' format.
        """
        data = self.get_cpi_data(start_date, end_date)
        observations = data['observations']
        
        if not observations:
            raise Exception("No CPI data found for the given date range")
        
        # Get first and last observation
        start_cpi = float(observations[0]['value'])
        end_cpi = float(observations[-1]['value'])
        
        # Calculate inflation
        inflation_rate = ((end_cpi - start_cpi) / start_cpi) * 100
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'start_cpi': start_cpi,
            'end_cpi': end_cpi,
            'inflation_rate': round(inflation_rate, 2)
        }
    
    def calculate_value(self, amount, start_date, end_date):
        data = self.get_cpi_data(start_date, end_date)
        observations = data['observations']
        
        if not observations:
            raise Exception("No CPI data found for the given date range")
            
        # Get first and last observation
        start_cpi = float(observations[0]['value'])
        end_cpi = float(observations[-1]['value'])
        print(f"start cpi {start_cpi}")
        print(f"end_cpi cpi {end_cpi}")
        # Calculate adjusted value
        adjusted_amount = amount * (end_cpi / start_cpi)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'original_amount': amount,
            'adjusted_amount': round(adjusted_amount, 2),
            'start_cpi': start_cpi,
            'end_cpi': end_cpi
        }
    
    def calculate_past_value(self, amount, start_date, end_date):
        data = self.get_cpi_data(start_date, end_date)
        observations = data['observations']
        
        if not observations:
            raise Exception("No CPI data found for the given date range")
            
        # Get first and last observation
        start_cpi = float(observations[0]['value'])
        end_cpi = float(observations[-1]['value'])
        
        # Calculate past value
        past_amount = amount * (start_cpi / end_cpi)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'current_amount': amount,
            'past_amount': round(past_amount, 2),
            'start_cpi': start_cpi,
            'end_cpi': end_cpi
        }

# Example usage
if __name__ == "__main__":
    api_key = ""
    calculator = FREDInflationCalculator(api_key)
    
    # Calculate what $1000 from 2020 would be worth in 2024
    result = calculator.calculate_value(1000, "2020-01-01", "2024-01-01")
    print(f"${result['original_amount']} in {result['start_date']} would be worth ${result['adjusted_amount']} in {result['end_date']}")
    
    # Calculate how much you'd need in 2020 to have $1000 in 2024
    reverse = calculator.calculate_past_value(1000, "2020-01-01", "2024-01-01")
    print(f"${reverse['current_amount']} in {reverse['end_date']} would be worth ${reverse['past_amount']} in {reverse['start_date']}")