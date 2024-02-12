data "aws_ami" "amazon_linux_2_ssm" {
  most_recent = true

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  filter {
    name   = "name"
    values = ["amzn2-ami-*-arm64-gp2"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["arm64"]
  }
}

data "aws_security_group" "default" {
  vpc_id = data.aws_vpc.this.id

  filter {
    name   = "group-name"
    values = ["default"]
  }
}

resource "aws_iam_role" "ec2_role" {
  name = "EC2_SSM_Role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_role_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.ec2_role.name
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "EC2_SSM_Instance_Profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_key_pair" "this" {
  key_name   = "${local.app_name}-bastion"
  public_key = tls_private_key.this.public_key_openssh
}

resource "tls_private_key" "this" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "this" {
  content  = tls_private_key.this.private_key_pem
  filename = "../${aws_key_pair.this.key_name}.key"

  provisioner "local-exec" {
    command = "chmod 600 ../${aws_key_pair.this.key_name}.key"
  }
}

resource "aws_instance" "ec2_instance" {
  ami           = data.aws_ami.amazon_linux_2_ssm.id
  instance_type = "t4g.nano"
  subnet_id     = data.aws_subnets.public.ids[0]
  vpc_security_group_ids = [
    aws_security_group.bastion.id,
    aws_security_group.opensearch_user.id,
  ]
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name
  key_name             = aws_key_pair.this.key_name

  tags = {
    Name = "${local.app_name}-bastion"
  }
}

# resource "aws_instance" "ec2_instance" {
#   ami           = data.aws_ami.amazon_linux_2_ssm.id
#   instance_type = "t4g.nano"
#   subnet_id     = data.aws_subnets.public.ids[0]
#   vpc_security_group_ids = [
#     aws_security_group.bastion.id,
#     aws_security_group.opensearch_user.id,
#   ]
#   iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name
#
#   tags = {
#     Name = "anime-recommender-bastion"
#   }
# }
