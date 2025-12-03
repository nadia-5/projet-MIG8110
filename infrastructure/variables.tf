variable "POSTGRES_HOST" {type = string}
variable "POSTGRES_PORT" {type = number}
variable "POSTGRES_DATABASE" {type = string}
variable "POSTGRES_USER" {type = string}
variable "POSTGRES_PASSWORD" {type = string}

variable "POSTGRES_DW_HOST" {type = string}
variable "POSTGRES_DW_PORT" {type = number}
variable "POSTGRES_DW_DATABASE" {type = string}
variable "POSTGRES_DW_USER" {type = string}
variable "POSTGRES_DW_PASSWORD" {type = string}

variable "MINIO_ENDPOINT" {type = string}
variable "MINIO_ACCESS_KEY" {type = string}
variable "MINIO_SECRET_KEY" {type = string}