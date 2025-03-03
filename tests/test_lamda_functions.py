from datetime import datetime, timedelta
from lambda_code_and_deps.index import is_this_a_valid_date, get_cpi_data, handler
from unittest.mock import patch, MagicMock

SAMPLE_FRED_RESPONSE = {
    "realtime_start": "2025-03-01",
    "realtime_end": "2025-03-01",
    "observation_start": "2020-01-01",
    "observation_end": "2020-03-01",
    "units": "lin",
    "output_type": 1,
    "file_type": "json",
    "order_by": "observation_date",
    "sort_order": "asc",
    "count": 3,
    "offset": 0,
    "limit": 100000,
    "observations": [
        {
            "realtime_start": "2025-03-01",
            "realtime_end": "2025-03-01",
            "date": "2020-01-01",
            "value": "259.127",
        },
        {
            "realtime_start": "2025-03-01",
            "realtime_end": "2025-03-01",
            "date": "2020-02-01",
            "value": "259.250",
        },
        {
            "realtime_start": "2025-03-01",
            "realtime_end": "2025-03-01",
            "date": "2020-03-01",
            "value": "258.076",
        },
    ],
}


def test_valid_date_function():
    assert is_this_a_valid_date("2024-02-29") == True  # Valid leap year date
    assert (
        is_this_a_valid_date((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
        == True
    )  # Valid past date
    assert is_this_a_valid_date("not-a-date") == False  # Invalid format
    assert is_this_a_valid_date("2025-13-01") == False  # Invalid month
    assert is_this_a_valid_date("2025-02-30") == False  # Invalid day
    assert (
        is_this_a_valid_date(datetime.now().strftime("%Y-%m-%d")) == True
    )  # Today's date should be valid
    assert (
        is_this_a_valid_date((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        == False
    )  # Tomorrow's date should be invalid


@patch("lambda_code_and_deps.index.requests.get")
def test_get_cpi_data(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_FRED_RESPONSE
    mock_post.return_value = mock_response
    assert get_cpi_data("2020-01-01", "2020-03-01") == SAMPLE_FRED_RESPONSE

    # error path
    mock_response.status_code = 400
    mock_response.text = "mock error"
    mock_post.return_value = mock_response

    try:
        get_cpi_data("2020-01-01", "2020-03-01")
    except Exception as e:
        assert str(e) == "FRED API request failed: mock error"


@patch("lambda_code_and_deps.index.requests.get")
def test_handler(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_FRED_RESPONSE
    mock_post.return_value = mock_response

    # inflation base path
    event = {"path": "/inflation", "body": {}}
    response = handler(event, None)
    assert response["statusCode"] == 200
    assert (
        response["body"]
        == '{"message": "Welcome to the inflation API", "available_endpoints": ' 
        + '["/inflation/calc?amount=1000&start_date=2020-01-01&end_date=2025-01-01", '
        + '"/inflation/reverse?amount=1000&start_date=2020-01-01&end_date=2025-01-01"]}'
    )

    # invalid path
    event = {"path": "/not_valid", "body": {}}
    response = handler(event, None)
    assert response["statusCode"] == 404
    assert response["body"] == '{"message": "Not Found", "path": "/not_valid"}'

    example_body = {
        "amount": 1000,
        "start_date": "2020-01-01",
        "end_date": "2020-03-01",
    }

    # inflation calc path
    event = {"path": "/inflation/calc", "queryStringParameters": example_body}
    response = handler(event, None)
    assert response["statusCode"] == 200
    assert (
        response["body"]
        == '{"start_date": "2020-01-01", "end_date": "2020-03-01", "original_amount": 1000.0, "adjusted_amount": 995.94}'
    )

    # reverse path
    event = {"path": "/inflation/reverse", "queryStringParameters": example_body}
    response = handler(event, None)
    assert response["statusCode"] == 200
    assert (
        response["body"]
        == '{"start_date": "2020-01-01", "end_date": "2020-03-01", "original_amount": 1000.0, "adjusted_amount": 1004.07}'
    )
