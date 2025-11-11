provider "aws" {
    region = "eu-west-2"
}

#security group for the database
resource "aws_security_group" "radas-group-project-sg" {
  name = "radas-group-project-sg"
  description = "security group for the museum database"
  vpc_id = var.vpc_id

}

#security group rule to allow ingress on port 1433 (MS SQL Server)
resource "aws_security_group_rule" "allow_TCP_1433_rule" {
    security_group_id = aws_security_group.radas-group-project-sg.id
    type              = "ingress"
    from_port         = 1433
    protocol          = "tcp"
    to_port           = 1433
    cidr_blocks       = ["0.0.0.0/0"]
}

#creating subnet group using the C20 VPC subnets
resource "aws_db_subnet_group" "radas-db-subnet-group" {
  name = "radas-db-subnet-group"
  subnet_ids = ["subnet-0c47ef6fc81ba084a", "subnet-00c68b4e0ee285460", "subnet-0c2e92c1b7b782543"]
}

#creating the S3 bucket to store the plants data
resource "aws_s3_bucket" "radas-plants-s3" {
  bucket = "radas-plants-s3"
  force_destroy = true
}

#specifies to not create a new version of the s3 every time the data is changed
resource "aws_s3_bucket_versioning" "radas-plants-s3-version" {
  bucket = aws_s3_bucket.radas-plants-s3.id
  versioning_configuration {
    status = "Disabled"
  }
}

#create ECR to store docker image
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

#outputs the ECR url
output "repository_url" {
  value = aws_ecr_repository.radas-plants-ecr.repository_url
}

#creates the ECS cluster for running tasks on
resource "aws_ecs_cluster" "radas-plants-ecs" {
  name = "radas-plants-ecs"
  setting {
    name = "containerInsights"
    value = "enabled"
  }
}

#specifies Fargate as the capacity provider for ECS
resource "aws_ecs_cluster_capacity_providers" "radas-plants-ecs-provider" {
  cluster_name = aws_ecs_cluster.radas-plants-ecs.name
  capacity_providers = ["FARGATE"]
  
}

#IAM role for executing tasks on the ECS
data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

#Creating the task definition family for the ECS
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

#Creating a service on the ECS to run
resource "aws_ecs_service" "radas-plants-ecs-service" {
  name = "radas-plants-ecs-service"
  cluster = aws_ecs_cluster.radas-plants-ecs.id
  task_definition = aws_ecs_task_definition.radas-plants-pipeline.arn
  desired_count = 1
  
  #specifying the network to use for the service
  network_configuration {
    subnets = aws_db_subnet_group.radas-db-subnet-group.subnet_ids
    security_groups = [aws_security_group.radas-group-project-sg.id]
  }
}

#creating a glue database for the crawler
resource "aws_glue_catalog_database" "radas-plants-glue-db" {
  name = "radas-plants-glue-db"
}

#creating an iam role for the crawler to use
resource "aws_iam_role" "radas-crawler-role" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      },
    ]
  })
}

#creating an attachment for the role's policy
resource "aws_iam_role_policy_attachment" "radas-glue-crawler-policy_attachment" {
  role = aws_iam_role.radas-crawler-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

#creating the policy for the crawler's IAM role
resource "aws_iam_role_policy" "radas-glue-crawler-policy" {
  role = aws_iam_role.radas-crawler-role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::radas-plants-s3",
          "arn:aws:s3:::radas-plants-s3/" #this one is to allow crawling of subfolders
        ]
      }
    ]
  })
}

#creating a glue crawler
resource "aws_glue_crawler" "radas-crawler" {
  name = "radas-crawler"
  database_name = "radas-plants-glue-db"
  role = aws_iam_role.radas-crawler-role.arn
  s3_target {
    path = "s3://radas-plants-s3"
  }
}