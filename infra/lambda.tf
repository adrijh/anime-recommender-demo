module "poller" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.app_name}-poller"
  description   = "Lambda polling data from external API"
  handler       = "app.lambda_handler"
  runtime       = "python3.12"
  timeout       = 900

  source_path   = "../src/poller"
  artifacts_dir = "../build/"

  vpc_subnet_ids = data.aws_subnets.private.ids
  vpc_security_group_ids = [
    aws_security_group.lambda.id,
  ]
  attach_network_policy = true

  environment_variables = {
    BUCKET_NAME         = aws_s3_bucket.this.bucket
    API_SECRETS_PARAM   = "/anime-recommender/myanimelist/secrets"
    API_REQUEST_SLEEP   = 1
    API_REQUEST_TIMEOUT = 10
    API_REQUEST_RETRIES = 5
  }

  attach_policy_statements = true
  policy_statements = {
    ssm_parameter = {
      effect    = "Allow",
      actions   = ["ssm:GetParameter"],
      resources = ["arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${local.app_name}*"]
    }
    s3 = {
      effect  = "Allow",
      actions = ["s3:ListBucket", "s3:*Object"],
      resources = [
        "arn:aws:s3:::${aws_s3_bucket.this.bucket}",
        "arn:aws:s3:::${aws_s3_bucket.this.bucket}/*",
      ]
    }
  }
}

module "indexer" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                           = "${local.app_name}-indexer"
  description                             = "Lambda inserting data from S3 to OpenSearch"
  handler                                 = "app.lambda_handler"
  runtime                                 = "python3.12"
  timeout                                 = 60
  reserved_concurrent_executions          = 1
  create_current_version_allowed_triggers = false

  source_path   = "../src/indexer"
  artifacts_dir = "../build/"

  vpc_subnet_ids = data.aws_subnets.private.ids
  vpc_security_group_ids = [
    aws_security_group.lambda.id,
    aws_security_group.opensearch_user.id,
  ]
  attach_network_policy = true

  environment_variables = {
    BUCKET_NAME = aws_s3_bucket.this.bucket
    # OPENSEARCH_ENDPOINT = "testing"
    OPENSEARCH_ENDPOINT = aws_opensearch_domain.this.endpoint
    INDEX_ALIAS         = "anime"
  }

  allowed_triggers = {
    sqs = {
      principal  = "sqs.amazonaws.com"
      source_arn = aws_sqs_queue.this.arn
    }
  }

  event_source_mapping = {
    sqs = {
      event_source_arn        = aws_sqs_queue.this.arn
      function_response_types = ["ReportBatchItemFailures"]
    }
  }

  attach_policy_statements = true
  policy_statements = {
    s3 = {
      effect  = "Allow",
      actions = ["s3:ListBucket", "s3:*Object"],
      resources = [
        "arn:aws:s3:::${aws_s3_bucket.this.bucket}",
        "arn:aws:s3:::${aws_s3_bucket.this.bucket}/*",
      ]
    }
  }
  attach_policies    = true
  number_of_policies = 1
  policies = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole",
  ]
}
