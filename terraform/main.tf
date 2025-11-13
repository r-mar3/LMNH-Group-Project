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

#create ECR to store etl docker image
resource "aws_ecr_repository" "radas-plants-etl-ecr" {
  name = "radas-plants-etl-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "radas-plants"
  }
}

#create ECR to store summary docker image
resource "aws_ecr_repository" "radas-plants-summary-ecr" {
  name = "radas-plants-summary-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "radas-plants"
  }
}

#create ECR to store dashboard docker image
resource "aws_ecr_repository" "radas-plants-dashboard-ecr" {
  name = "radas-plants-dashboard-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "radas-plants"
  }
}

#create ECR to store notifications docker image
resource "aws_ecr_repository" "radas-plants-notifications-ecr" {
  name = "radas-plants-notifications-ecr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project = "radas-plants"
  }
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

#Creating the task definition family for the ETL
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

#Creating the task definition family for the summary
resource "aws_ecs_task_definition" "radas-plants-summary" {
  family = "radas-plants-summary-family"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]

container_definitions = jsonencode([
    {
      name      = "radas-summary-task"
      image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/radas-plants-summary-ecr:latest"
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


#creating iam role for the lambda that runs ETL container
resource "aws_iam_role" "radas-etl-lambda-iam-role" {
  name = "radas-etl-lambda-iam-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

#attaching execution role to ETL Lambda's IAM role
resource "aws_iam_role_policy_attachment" "radas-lambda-etl-policy-attachment" {
  role = aws_iam_role.radas-etl-lambda-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "radas-lambda-etl-allow-ecr-access" {
  role = aws_iam_role.radas-etl-lambda-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

#adding policies to ETL Lambda's IAM role to allow access to RDS
resource "aws_iam_role_policy" "radas-lambda-rds-policy" {
  name = "radas-lambda-rds-policy"
  role = aws_iam_role.radas-etl-lambda-iam-role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:Connect",
          "rds:DescribeDBProxies",
          "rds:DescribeDBProxyTargets"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = ["secretsmanager:GetSecretValue"],
        Resource = "arn:aws:secretsmanager:eu-west-2:129033205317:secret:*"
      }
    ]
  })
}

#creating Lambda function to run ETL
resource "aws_lambda_function" "radas-lambda-etl-pipeline" {
  function_name = "radas-lambda-etl-pipeline"
  role = aws_iam_role.radas-etl-lambda-iam-role.arn
  package_type = "Image"
  image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/radas-plants-etl-ecr:latest"

  architectures = ["x86_64"]

}

#IAM role for the summary data Lambda
resource "aws_iam_role" "radas-summary-lambda-iam-role" {
  name = "radas-summary-lambda-iam-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

#attach execution role to the Lambda's IAM role
resource "aws_iam_role_policy_attachment" "radas-lambda-summary-policy-attachment" {
  role = aws_iam_role.radas-summary-lambda-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "radas-lambda-summary-allow-ecr-access" {
  role = aws_iam_role.radas-summary-lambda-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

#attaching permissions to read and write to S3
resource "aws_iam_role_policy" "radas-lambda-s3-policy" {
  name = "radas-lambda-s3-policy"
  role = aws_iam_role.radas-summary-lambda-iam-role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::radas-plants-s3",
          "arn:aws:s3:::radas-plants-s3/*"
        ]
      },
    ]
  })
}

#creating lambda function for running the summary data container
resource "aws_lambda_function" "radas-lambda-summary" {
  function_name = "radas-lambda-summary"
  role = aws_iam_role.radas-summary-lambda-iam-role.arn
  package_type = "Image"
  image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/radas-plants-summary-ecr:latest"

  architectures = ["x86_64"]

}


#creating iam role for the lambda that runs dashboard container
resource "aws_iam_role" "radas-dashboard-iam-role" {
  name = "radas-dashboard-iam-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

#attaching execution role to ETL Lambda's IAM role
resource "aws_iam_role_policy_attachment" "radas-lambda-dashboard-policy-attachment" {
  role = aws_iam_role.radas-dashboard-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "radas-lambda-dashboard-allow-ecr-access" {
  role = aws_iam_role.radas-dashboard-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

#creating lambda function for running the summary data container
resource "aws_lambda_function" "radas-lambda-dashboard" {
  function_name = "radas-lambda-dashboard"
  role = aws_iam_role.radas-dashboard-iam-role.arn
  package_type = "Image"
  image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/radas-plants-dashboard-ecr:latest"

  architectures = ["x86_64"]

}

#policy document for the scheduler
data "aws_iam_policy_document" "radas-etl-scheduler-policy-doc" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

#iam role for the scheduler
resource "aws_iam_role" "radas-etl-scheduler-role" {
  name = "radas-etl-scheduler-role"
  assume_role_policy = data.aws_iam_policy_document.radas-etl-scheduler-policy-doc.json
}

#allowing scheduler to invoke lambda
resource "aws_iam_policy" "radas-etl-scheduler-policy" {
  name = "radas-etl-scheduler-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:InvokeAsync"
        ]
        Resource = "*"
      }
    ]
  })
}




