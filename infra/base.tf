locals {
  prefix   = "bluetab"
  app_name = "anime-recommender"
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

data "aws_vpc" "this" {
  tags = {
    Name = "*bluetab-aws-practice*"
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.this.id]
  }

  tags = {
    Name = "*private*"
  }
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.this.id]
  }

  tags = {
    Name = "*public*"
  }
}

resource "aws_s3_bucket" "this" {
  bucket = "${local.prefix}-${local.app_name}"
}

data "aws_iam_policy_document" "queue" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["sqs:SendMessage"]
    resources = ["arn:aws:sqs:*:*:${local.app_name}"]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_s3_bucket.this.arn]
    }
  }
}

resource "aws_sqs_queue" "this" {
  name                       = local.app_name
  policy                     = data.aws_iam_policy_document.queue.json
  visibility_timeout_seconds = 180
}

resource "aws_s3_bucket_notification" "this" {
  bucket = aws_s3_bucket.this.id

  queue {
    queue_arn     = aws_sqs_queue.this.arn
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ".json"
  }
}
