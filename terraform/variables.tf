variable "cluster_name" {
  description = "Name of the local kind cluster"
  type        = string
  default     = "secureship"
}

variable "worker_count" {
  description = "Number of worker nodes (pods of the app are spread across them)"
  type        = number
  default     = 2
}

variable "grafana_admin_password" {
  description = "Grafana admin password (local demo only)"
  type        = string
  default     = "secureship"
  sensitive   = true
}
