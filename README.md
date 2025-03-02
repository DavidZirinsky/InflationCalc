https://fskgad1wub.execute-api.us-east-1.amazonaws.com/prod/inflation/calc?amount=1234&start_date=2020-01-01&end_date=2025-01-01
https://fskgad1wub.execute-api.us-east-1.amazonaws.com/prod/inflation/reverse?amount=1234&start_date=2020-01-01&end_date=2025-01-01


aws lambda invoke --function-name inflation_lambda response.json


I did: pip install requests -t .


zip -r ../infra/lambda.zip ./*