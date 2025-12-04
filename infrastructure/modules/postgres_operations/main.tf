terraform {
  required_providers {
    postgresql = {
      source  = "doctolib/postgresql"
    }
  }
  required_version = ">= 1.3.0"
}