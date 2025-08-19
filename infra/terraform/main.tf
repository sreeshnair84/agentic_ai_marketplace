resource "aws_s3_bucket" "agenticai_bucket" {
  bucket = "agenticai-multiagent-platform-bucket"
  acl    = "private"

  tags = {
    Name        = "Agentic AI Acceleration Bucket"
    Environment = "development"
  }
}

resource "aws_dynamodb_table" "agents_table" {
  name         = "Agents"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "agent_id"

  attribute {
    name = "agent_id"
    type = "S"
  }

  attribute {
    name = "skill"
    type = "S"
  }

  tags = {
    Name        = "Agents Table"
    Environment = "development"
  }
}

resource "aws_dynamodb_table" "tools_table" {
  name         = "Tools"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "tool_id"

  attribute {
    name = "tool_id"
    type = "S"
  }

  tags = {
    Name        = "Tools Table"
    Environment = "development"
  }
}

resource "aws_lambda_function" "agent_function" {
  function_name = "AgentFunction"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  role          = aws_iam_role.lambda_exec.arn
  s3_bucket     = aws_s3_bucket.agenticai_bucket.bucket
  s3_key        = "path/to/your/lambda/code.zip"

  environment = {
    DYNAMODB_AGENTS_TABLE = aws_dynamodb_table.agents_table.name
    DYNAMODB_TOOLS_TABLE  = aws_dynamodb_table.tools_table.name
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect    = "Allow"
        Sid       = ""
      },
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_policy" {
  name       = "lambda_policy_attachment"
  roles      = [aws_iam_role.lambda_exec.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

output "bucket_name" {
  value = aws_s3_bucket.agenticai_bucket.bucket
}

output "agents_table_name" {
  value = aws_dynamodb_table.agents_table.name
}

output "tools_table_name" {
  value = aws_dynamodb_table.tools_table.name
}

output "lambda_function_name" {
  value = aws_lambda_function.agent_function.function_name
}