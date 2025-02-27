import json

def lambda_handler(event, context):
    # Retrieve the path from the event object
    path = event['resource']
    
    # Check the path and route the request to the appropriate handler
    if path == "/inflation/calc":
        return calc_inflation(event)
    elif path == "/inflation/reverse":
        return reverse_inflation(event)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Not Found')
        }

def calc_inflation(event):
    # Your logic for /calc endpoint (e.g., inflation calculation)
    data = {
        "message": "Inflation calculation result",
        "calculation": 10  # Example calculation
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }

def reverse_inflation(event):
    # Your logic for /reverse endpoint (e.g., reversing inflation calculation)
    data = {
        "message": "Reverse inflation calculation result",
        "calculation": -10  # Example reversed calculation
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }