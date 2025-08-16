variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "The username for the database."
  type        = string
}

variable "db_password" {
  description = "The password for the database."
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "The name of the database."
  type        = string
  default     = "lcnc_multiagent_db"
}

variable "instance_type" {
  description = "The type of EC2 instance to use."
  type        = string
  default     = "t2.micro"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "The CIDR block for the subnet."
  type        = string
  default     = "10.0.1.0/24"
}

variable "key_name" {
  description = "The name of the key pair to use for SSH access."
  type        = string
}

variable "allowed_ips" {
  description = "The IP addresses allowed to access the application."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}