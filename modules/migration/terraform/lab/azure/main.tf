locals {
  tags = {
    Workshop = "azure-migration-terraform"
    LabId    = var.lab_id
  }
}

resource "azurerm_resource_group" "workshop" {
  name     = "rg-amw-tf-${var.lab_id}"
  location = var.location
  tags     = local.tags
}

resource "azurerm_container_app_environment" "workshop" {
  name                = "env-amw-tf-${var.lab_id}"
  location            = azurerm_resource_group.workshop.location
  resource_group_name = azurerm_resource_group.workshop.name
  tags                = local.tags

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
}

module "app" {
  source  = "Azure/avm-res-app-containerapp/azurerm"
  version = "0.9.0"

  name                                  = "app-amw-tf-${var.lab_id}"
  resource_group_name                   = azurerm_resource_group.workshop.name
  container_app_environment_resource_id = azurerm_container_app_environment.workshop.id
  enable_telemetry                      = false
  revision_mode                         = "Single"
  tags                                  = local.tags

  managed_identities = {
    user_assigned_resource_ids = [var.pull_identity_id]
  }
  registries = [{
    server   = var.registry_server
    identity = var.pull_identity_id
  }]
  ingress = {
    external_enabled = true
    target_port      = 8080
    traffic_weight = [{
      latest_revision = true
      percentage      = 100
    }]
  }
  template = {
    min_replicas = 1
    max_replicas = 1
    containers = [{
      name   = "workshop"
      image  = var.container_image
      cpu    = 0.25
      memory = "0.5Gi"
    }]
  }
}
