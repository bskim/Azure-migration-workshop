output "illustrative_app_url" {
  description = "Illustrative endpoint only; no instance is created in this workshop."
  value       = "http://${aws_instance.app.public_ip}:8080"
}
