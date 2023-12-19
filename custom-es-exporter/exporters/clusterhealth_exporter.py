import time
import os

from elasticsearch import Elasticsearch
from prometheus_client import start_http_server, Gauge


# Password for the 'elastic' user generated by Elasticsearch
ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD")
ELASTIC_HOST = os.environ.get("ELASTIC_HOST")

# import os
# # Get the absolute path to the script's directory
# script_dir = os.path.dirname(os.path.abspath(__file__))
# # Construct the absolute path to the CA certificate file
# ca_certs_path = os.path.join(script_dir, "../http_ca.crt")

# Create the client instance
eclient = Elasticsearch(
    ELASTIC_HOST,
    ca_certs="/escerts/certs/ca/ca.crt",
    basic_auth=("elastic", ELASTIC_PASSWORD)
)


# Prometheus metrics
cluster_health_metric = Gauge("elasticsearch_cluster_health", "Overall health status of the Elasticsearch cluster (0: green, 1: yellow, 2: red)")
active_primary_shards_metric = Gauge("elasticsearch_active_primary_shards", "Number of active primary shards")
active_shards_metric = Gauge("elasticsearch_active_shards", "Total number of active shards (primary and replica)")
relocating_shards_metric = Gauge("elasticsearch_relocating_shards", "Number of shards currently relocating")

def update_metrics():
    # Retrieve cluster health information
    cluster_health = eclient.cluster.health()
    print(cluster_health)
    active_primary_shards = cluster_health["active_primary_shards"]
    active_shards = cluster_health["active_shards"]
    relocating_shards = cluster_health["relocating_shards"]

    # Update Prometheus metrics
    cluster_health_metric.set(0 if cluster_health["status"] == "green" else 1 if cluster_health["status"] == "yellow" else 2)
    active_primary_shards_metric.set(active_primary_shards)
    active_shards_metric.set(active_shards)
    relocating_shards_metric.set(relocating_shards)


if __name__ == "__main__":
    # Start the Prometheus metrics HTTP server on port 8000
    start_http_server(8000)

    # Periodically update metrics (every 30 seconds in this example)
    while True:
        update_metrics()
        time.sleep(30)
