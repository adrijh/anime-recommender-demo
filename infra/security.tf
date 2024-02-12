resource "aws_security_group" "opensearch" {
  name   = "${local.app_name}-opensearch"
  vpc_id = data.aws_vpc.this.id
}

resource "aws_security_group_rule" "opensearch_ingress" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.opensearch_user.id
  security_group_id        = aws_security_group.opensearch.id
}

resource "aws_security_group_rule" "all_egress" {
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.opensearch.id
}

resource "aws_security_group" "opensearch_user" {
  name   = "${local.app_name}-user"
  vpc_id = data.aws_vpc.this.id
}

resource "aws_security_group_rule" "opensearch_egress" {
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.opensearch.id
  security_group_id        = aws_security_group.opensearch_user.id
}

resource "aws_security_group" "bastion" {
  name   = "${local.app_name}-bastion"
  vpc_id = data.aws_vpc.this.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "lambda" {
  name   = "${local.app_name}-lambda"
  vpc_id = data.aws_vpc.this.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
