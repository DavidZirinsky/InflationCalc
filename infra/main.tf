provider "aws" {
  region = "us-east-1"
}

# IAM Role for Lambda Execution
resource "aws_iam_role" "lambda_role" {
  name = "inflation_lambda_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "lambda_basic_execution" {
  name       = "lambda_basic_execution"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "inflation" {
  filename      = "lambda.zip"
  function_name = "inflation_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"
  source_code_hash = filebase64sha256("lambda.zip")
}

# API Gateway
resource "aws_api_gateway_rest_api" "inflation_api" {
  name        = "inflationAPI"
  description = "API for inflation Lambda"
}

# API Gateway Resource ("/inflation")
resource "aws_api_gateway_resource" "inflation_resource" {
  rest_api_id = aws_api_gateway_rest_api.inflation_api.id
  parent_id   = aws_api_gateway_rest_api.inflation_api.root_resource_id
  path_part   = "inflation"
}

# API Gateway Method (GET)
resource "aws_api_gateway_method" "get_inflation" {
  rest_api_id   = aws_api_gateway_rest_api.inflation_api.id
  resource_id   = aws_api_gateway_resource.inflation_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# Integration: Connect API Gateway to Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.inflation_api.id
  resource_id = aws_api_gateway_resource.inflation_resource.id
  http_method = aws_api_gateway_method.get_inflation.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.inflation.invoke_arn
}

# Deploy API Gateway
resource "aws_api_gateway_deployment" "inflation_deployment" {
  depends_on = [aws_api_gateway_integration.lambda_integration]
  rest_api_id = aws_api_gateway_rest_api.inflation_api.id
}

# Allow API Gateway to Invoke Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.inflation.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.inflation_api.execution_arn}/*/*"
}

# Output the API URL
output "invoke_url" {
    value = "${aws_api_gateway_stage.prod.invoke_url}/inflation"
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.inflation_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.inflation_api.id
  stage_name    = "prod"
}

# API Gateway Method Settings (for rate limiting)
resource "aws_api_gateway_method_settings" "settings" {
  rest_api_id = aws_api_gateway_rest_api.inflation_api.id
  stage_name  = aws_api_gateway_stage.prod.stage_name
  method_path = "*/*"  # This applies to all methods on all resources

  settings {
    throttling_rate_limit  = 2 # per second
    throttling_burst_limit = 5
  }
}