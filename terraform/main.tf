terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.18"
    }
  }

  required_version = ">= 1.2.0"
}

# create lambda log group resources 
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14
}


# create IAM role resources
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "${var.lambda_function_name}-iam-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}


# create lambda policy resources
data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}


resource "aws_iam_policy" "lambda_logging_policy" {
  name        = "${var.lambda_function_name}_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

# Attach the policy to lambda role
resource "aws_iam_role_policy_attachment" "lambda_logs_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging_policy.arn
}


# Create lambda function
resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_function_name
  timeout      = 120
  memory_size  = 720
  image_uri     = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.ecr_repository_name}:latest"
  package_type  = "Image"
  architectures = ["x86_64"]
  depends_on = [
    aws_cloudwatch_log_group.lambda_log_group,
    aws_iam_role_policy_attachment.lambda_logs_policy_attachment,
  ]
  role = aws_iam_role.iam_for_lambda.arn

  ephemeral_storage {
    size = 512
  }
}