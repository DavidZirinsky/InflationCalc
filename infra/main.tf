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
  name = "lambda_basic_execution"
  roles = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "inflation" {
  filename = "lambda.zip"
  function_name = "inflation_lambda"
  role = aws_iam_role.lambda_role.arn
  handler = "index.handler"
  runtime = "python3.9"
  source_code_hash = filebase64sha256("lambda.zip")
  # ENV Variable
  environment {
    variables = {
      FRED_API_KEY = var.FRED_API_KEY
    }
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "inflation_api" {
  name = "inflationAPI"
  description = "API for inflation Lambda"
}

# Create a single proxy resource at the root level
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.inflation_api.id
  parent_id   = aws_api_gateway_rest_api.inflation_api.root_resource_id
  path_part   = "{proxy+}"
}

# ANY method to catch all HTTP methods
resource "aws_api_gateway_method" "proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.inflation_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

# Proxy integration with Lambda
resource "aws_api_gateway_integration" "lambda_proxy_integration" {
  rest_api_id = aws_api_gateway_rest_api.inflation_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_method.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.inflation.invoke_arn
}

# Also handle the root path "/" 
resource "aws_api_gateway_method" "root_method" {
  rest_api_id   = aws_api_gateway_rest_api.inflation_api.id
  resource_id   = aws_api_gateway_rest_api.inflation_api.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "root_integration" {
  rest_api_id = aws_api_gateway_rest_api.inflation_api.id
  resource_id = aws_api_gateway_rest_api.inflation_api.root_resource_id
  http_method = aws_api_gateway_method.root_method.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.inflation.invoke_arn
}

# Deploy API Gateway
resource "aws_api_gateway_deployment" "inflation_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_proxy_integration,
    aws_api_gateway_integration.root_integration
  ]
  
  rest_api_id = aws_api_gateway_rest_api.inflation_api.id
  
  # Add a trigger that forces new deployment each time
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.proxy.id,
      aws_api_gateway_method.proxy_method.id,
      aws_api_gateway_integration.lambda_proxy_integration.id,
      aws_api_gateway_method.root_method.id,
      aws_api_gateway_integration.root_integration.id
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# Allow API Gateway to Invoke Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.inflation.function_name
  principal     = "apigateway.amazonaws.com"
  
  # The /* part allows invocation from any stage, method and resource path
  source_arn = "${aws_api_gateway_rest_api.inflation_api.execution_arn}/*/*"
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
  method_path = "*/*" # This applies to all methods on all resources
  
  settings {
    throttling_rate_limit  = 2 # per second
    throttling_burst_limit = 5
  }
}

variable "FRED_API_KEY" {
  description = "API key for the service"
  type        = string
  sensitive   = true  # Marks as sensitive to hide in logs
}


# Output the API URLs
output "api_base_url" {
  value = aws_api_gateway_stage.prod.invoke_url
}

output "inflation_endpoint" {
  value = "${aws_api_gateway_stage.prod.invoke_url}/inflation"
}

output "inflation_calc_endpoint" {
  value = "${aws_api_gateway_stage.prod.invoke_url}/inflation/calc"
}