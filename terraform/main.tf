provider "aws" {
    region = "eu-west-2"
}

resource "aws_security_group" "radas-group-project-sg" {
  name = "radas-group-project-sg"
  description = "security group for the museum database"
  vpc_id = var.vpc_id

}
resource "aws_security_group_rule" "allow_TCP_1433_rule" {
    security_group_id = aws_security_group.radas-group-project-sg.id
    type              = "ingress"
    from_port         = 1433
    protocol          = "tcp"
    to_port           = 1433
    cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_db_subnet_group" "radas-db-subnet-group" {
  name = "radas-db-subnet-group"
  subnet_ids = ["subnet-0c47ef6fc81ba084a", "subnet-00c68b4e0ee285460", "subnet-0c2e92c1b7b782543"]
}

resource "aws_s3_bucket" "radas-plants-s3" {
  bucket = "radas-plants-s3"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "radas-plants-s3-version" {
  bucket = aws_s3_bucket.radas-plants-s3.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_ecr_repository" "radas-plants-ecr" {
  name = "radas-plants-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "radas-plants"
  }
}

output "repository_url" {
  value = aws_ecr_repository.radas-plants-ecr.repository_url
}

resource "aws_ecs_cluster" "radas-plants-ecs" {
  name = "radas-plants-ecs"
  setting {
    name = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "radas-plants-ecs-provider" {
  cluster_name = aws_ecs_cluster.radas-plants-ecs.name
  capacity_providers = ["FARGATE"]
  
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "radas-plants-pipeline" {
  family = "radas-plants-pipeline-family"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]

container_definitions = jsonencode([
    {
      name      = "ronn-pipeline-task"
      image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/radas-plants-etl:latest"
      essential = true
      environment = [ 
        {name = "DB_HOST", value = var.DB_HOST},
        {name = "DB_PORT", value = var.DB_PORT},
        {name = "DB_NAME", value = var.DB_NAME},
        {name = "DB_USER", value = var.DB_USERNAME},
        {name = "DB_PASSWORD", value = var.DB_PASSWORD},
        {name = "ACCESS_KEY", value = var.AWS_ACCESS_KEY_ID},
        {name = "SECRET_ACCESS_KEY", value = var.AWS_SECRET_ACCESS_KEY},
        {name = "REGION", value = var.AWS_DEFAULT_REGION},
        {name = "BUCKET_NAME", value = var.BUCKET_NAME}
      ]
    }
  ])

  cpu = 512
  memory = 1024
  task_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
}

resource "aws_ecs_service" "radas-plants-ecs-service" {
  name = "radas-plants-ecs-service"
  cluster = aws_ecs_cluster.radas-plants-ecs.id
  task_definition = aws_ecs_task_definition.radas-plants-pipeline.arn
  desired_count = 1
  
  network_configuration {
    subnets = aws_db_subnet_group.radas-db-subnet-group.subnet_ids
    security_groups = [aws_security_group.radas-group-project-sg.id]
  }
}

