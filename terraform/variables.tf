variable "username" {
  type = string
  sensitive = true
}

variable "password" {
  type = string
  sensitive = true
}

variable "vpc_id" {
  type        = string
  description = "C20 VPC id where I want my resources to go"
  default     = "vpc-01b7a51a09d27de04"
}

variable "DB_HOST" {
  type = string
  sensitive = true
}

variable "DB_PORT" {
  type = string
  sensitive = true
}

variable "DB_NAME" {
  type = string
  sensitive = true
}

variable "DB_USERNAME" {
  type = string
  sensitive = true
}

variable "DB_PASSWORD" {
  type = string
  sensitive = true
}

variable "AWS_ACCESS_KEY_ID" {
  type = string
  sensitive = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
  sensitive = true
}

variable "AWS_DEFAULT_REGION" {
  type = string
  sensitive = true
}

variable "BUCKET_NAME" {
  type = string
  sensitive = true
}
