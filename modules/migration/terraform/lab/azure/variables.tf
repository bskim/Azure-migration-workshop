variable "subscription_id" {
  description = "Approved sandbox subscription ID."
  type        = string
}

variable "location" {
  description = "Approved region supporting Container Apps Consumption."
  type        = string
}

variable "lab_id" {
  description = "Unique lowercase eight-character lab suffix."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{8}$", var.lab_id))
    error_message = "Use eight lowercase letters or digits for lab_id."
  }
}

variable "container_image" {
  description = "Existing workshop image, preferably referenced by sha256 digest."
  type        = string
}

variable "registry_server" {
  description = "Existing ACR login server without a URL scheme."
  type        = string
}

variable "pull_identity_id" {
  description = "Existing user-assigned identity resource ID with AcrPull on the registry."
  type        = string
}
