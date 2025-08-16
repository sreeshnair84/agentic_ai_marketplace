provider "azurerm" {
  features {}
}

provider "aws" {
  region = "us-west-2"
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

# Define any additional providers as needed
# For example, if using a database provider
provider "postgresql" {
  host     = var.db_host
  port     = var.db_port
  username = var.db_username
  password = var.db_password
  database = var.db_name
}