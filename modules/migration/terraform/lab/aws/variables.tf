variable "region" {
  description = "Illustrative AWS region. This sample is not deployed."
  type        = string
  default     = "us-east-1"
}

variable "ami_id" {
  description = "Amazon Linux 2023 x86_64 AMI placeholder; no live lookup is performed."
  type        = string
  default     = "ami-00000000000000000"
}

variable "client_cidr" {
  description = "Documentation-only client address, not an open Internet ingress rule."
  type        = string
  default     = "192.0.2.1/32"
}

variable "container_image" {
  description = "Illustrative public image reference; replace only in an approved deployment exercise."
  type        = string
  default     = "example.invalid/workshop/app:0.1.0"

  validation {
    condition     = can(regex("^[a-zA-Z0-9._:/@-]+$", var.container_image))
    error_message = "The image reference must not contain shell metacharacters or whitespace."
  }
}
