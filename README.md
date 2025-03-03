# Inflation Calculator 

A full stack web app that uses the FRED api to calculate inflation. This involves a React Frontend, a python backend, and terraform for IaC to configure the AWS lambda the backend runs on. 
This can be viewed at:
https://davidzirinsky.com/inflation/

<br>
<br>

<img src="github_assets/app.png" /> 

<br>

## Deploy the backend
Go to the `lambda_code_and_deps` folder:
```
cd lambda_code_and_deps/
```

Lambda dependencies can be tricky, so run this command to install the `requests` module:
```
pip install requests -t .
```

Zip it on up:
```
zip -r ../infra/lambda.zip ./*
```

Then go to the `infra` folder and run this:
```
cd ../infra
terraform plan
terraform apply
```

As a debug step you can always to this, the advatages of this command are if networking isn't set up you can still test that the lambda is running. The AWS console is also quite helpful
```
aws lambda invoke --function-name inflation_lambda response.json
```
## Running the Frontend

In the frontend directory, you can run:

build:
### `npm start`
test:
### `npm test`

prod build:
### `npm run build`


https://fskgad1wub.execute-api.us-east-1.amazonaws.com/prod/inflation/calc?amount=1234&start_date=2020-01-01&end_date=2025-01-01
https://fskgad1wub.execute-api.us-east-1.amazonaws.com/prod/inflation/reverse?amount=1234&start_date=2020-01-01&end_date=2025-01-01


aws lambda invoke --function-name inflation_lambda response.json


I did: pip install requests -t .


zip -r ../infra/lambda.zip ./*