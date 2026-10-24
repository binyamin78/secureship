output "kubeconfig" {
  description = "Use with: export KUBECONFIG=$(terraform output -raw kubeconfig)"
  value       = kind_cluster.this.kubeconfig_path
}

output "urls" {
  value = {
    app          = "http://localhost:8080"
    grafana      = "http://localhost:3000  (admin / see grafana_admin_password)"
    prometheus   = "http://localhost:9090"
    alertmanager = "http://localhost:9093"
  }
}
