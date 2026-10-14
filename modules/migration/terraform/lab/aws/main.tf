resource "aws_vpc" "workshop" {
  cidr_block           = "10.40.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "workshop-source", Purpose = "instruction-only" }
}

resource "aws_subnet" "workshop" {
  vpc_id                  = aws_vpc.workshop.id
  cidr_block              = "10.40.1.0/24"
  map_public_ip_on_launch = true
}

resource "aws_internet_gateway" "workshop" {
  vpc_id = aws_vpc.workshop.id
}

resource "aws_route_table" "workshop" {
  vpc_id = aws_vpc.workshop.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.workshop.id
  }
}

resource "aws_route_table_association" "workshop" {
  subnet_id      = aws_subnet.workshop.id
  route_table_id = aws_route_table.workshop.id
}

resource "aws_security_group" "app" {
  name   = "workshop-app"
  vpc_id = aws_vpc.workshop.id

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.client_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app" {
  ami                         = var.ami_id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.workshop.id
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    encrypted = true
  }

  user_data = <<-USER_DATA
    #!/bin/bash
    set -eu
    dnf install -y docker
    systemctl enable --now docker
    docker run -d --name workshop-app --restart unless-stopped \
      -p 8080:8080 '${var.container_image}'
  USER_DATA

  depends_on = [aws_route_table_association.workshop]
  tags       = { Name = "workshop-app", Purpose = "instruction-only" }
}
