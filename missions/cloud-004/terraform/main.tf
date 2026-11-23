terraform {
  required_version = ">= 1.5"
}

# Built-in resource type: no external provider, cloud bill or credentials.
resource "terraform_data" "local_probe" {
  input = "atlas-retail-safe-example"
}

output "probe_value" {
  value = terraform_data.local_probe.output
}
