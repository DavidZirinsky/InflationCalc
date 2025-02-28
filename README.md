https://rz9r7700gh.execute-api.us-east-1.amazonaws.com/prod/inflation

zip infra/lambda.zip index.py

zip lambda.zip ../index.py

aws lambda invoke --function-name inflation_lambda response.json