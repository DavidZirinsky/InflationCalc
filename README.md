https://rz9r7700gh.execute-api.us-east-1.amazonaws.com/prod/inflation/calc?amount=1234&start_date=2020-01-01&end_date=2025-01-01

zip infra/lambda.zip index.py

zip lambda.zip ../index.py

aws lambda invoke --function-name inflation_lambda response.json