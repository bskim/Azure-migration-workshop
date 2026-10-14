output "app_url" {
  description = "HTTPS endpoint after an approved Azure deployment."
  value       = module.app.fqdn_url
}

output "resource_group_name" {
  value = azurerm_resource_group.workshop.name
}
