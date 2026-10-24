# SecureShip - station 3: one `terraform apply` builds the whole platform.

# ---------- The Kubernetes cluster (kind = Kubernetes inside Docker) ----------
resource "kind_cluster" "this" {
  name            = var.cluster_name
  wait_for_ready  = true
  kubeconfig_path = abspath("${path.module}/kubeconfig")

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"

      # NodePort services -> localhost on the laptop
      extra_port_mappings {
        container_port = 30080 # DevBoard app
        host_port      = 8080
      }
      extra_port_mappings {
        container_port = 30300 # Grafana
        host_port      = 3000
      }
      extra_port_mappings {
        container_port = 30090 # Prometheus
        host_port      = 9090
      }
      extra_port_mappings {
        container_port = 30093 # Alertmanager
        host_port      = 9093
      }
    }

    dynamic "node" {
      for_each = range(var.worker_count)
      content {
        role = "worker"
      }
    }
  }
}

provider "helm" {
  kubernetes = {
    host                   = kind_cluster.this.endpoint
    client_certificate     = kind_cluster.this.client_certificate
    client_key             = kind_cluster.this.client_key
    cluster_ca_certificate = kind_cluster.this.cluster_ca_certificate
  }
}

# ---------- metrics-server: CPU/memory numbers for the HPA ----------
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  version    = "3.14.0"
  namespace  = "kube-system"

  # kind's kubelets use self-signed certificates
  values = [yamlencode({ args = ["--kubelet-insecure-tls"] })]
}

# ---------- Prometheus + Grafana + Alertmanager (station 4) ----------
resource "helm_release" "monitoring" {
  name             = "monitoring"
  repository       = "oci://ghcr.io/prometheus-community/charts"
  chart            = "kube-prometheus-stack"
  version          = "92.13.1"
  namespace        = "monitoring"
  create_namespace = true
  timeout          = 900

  values = [file("${path.module}/monitoring-values.yaml")]

  set_sensitive = [{
    name  = "grafana.adminPassword"
    value = var.grafana_admin_password
  }]
}
