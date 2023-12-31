import time
import os

from elasticsearch import Elasticsearch
from prometheus_client import start_http_server, Gauge


# Password for the 'elastic' user generated by Elasticsearch
ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD")
ELASTIC_HOST = os.environ.get("ELASTIC_HOST")

# Create the client instance
eclient = Elasticsearch(
    ELASTIC_HOST,
    ca_certs="/escerts/ca/ca.crt",
    basic_auth=("elastic", ELASTIC_PASSWORD)
)


# Prometheus metrics
cluster_health_metric = Gauge(
    "elasticsearch_cluster_health", 
    "Overall health status of the Elasticsearch cluster (0: green, 1: yellow, 2: red)")
active_primary_shards_metric = Gauge(
    "elasticsearch_active_primary_shards", 
    "Number of active primary shards")
active_shards_metric = Gauge(
    "elasticsearch_active_shards", 
    "Total number of active shards (primary and replica)")
relocating_shards_metric = Gauge(
    "elasticsearch_relocating_shards",
    "Number of shards currently relocating")
number_of_nodes_metric = Gauge(
    "elasticsearch_number_of_nodes",
    "Total Number of Nodes")
active_shards_percent_as_number_metric = Gauge(
    "elasticsearch_active_shards_percent_as_number",
    "Active shards percentage as a number")

index_documents_metric = Gauge(
    "elasticsearch_index_documents", 
    "Number of documents in an index", 
    labelnames=["index"])
index_size_bytes_metric = Gauge(
    "elasticsearch_index_size_bytes", 
    "Size of an index in bytes", 
    labelnames=["index"])
index_search_query_total_metric = Gauge(
    "elasticsearch_index_search_query_total", 
    "Total number of search queries on an index", 
    labelnames=["index"])
index_search_query_time_seconds_metric = Gauge(
    "elasticsearch_index_search_query_time_seconds", 
    "Total time spent on search queries in seconds", 
    labelnames=["index"])


def update_metrics():
    # Retrieve cluster health information
    cluster_health = eclient.cluster.health()
    active_primary_shards = cluster_health["active_primary_shards"]
    active_shards = cluster_health["active_shards"]
    relocating_shards = cluster_health["relocating_shards"]
    number_of_nodes = cluster_health["number_of_nodes"]
    active_shards_percent_as_number = cluster_health["active_shards_percent_as_number"]
    # Retrieve index metrics from Elasticsearch
    indices_stats = eclient.indices.stats(metric="docs,store,search")

    # Update Prometheus metrics
    cluster_health_metric.set(0 if cluster_health["status"] == "green" else 1 if cluster_health["status"] == "yellow" else 2)
    active_primary_shards_metric.set(active_primary_shards)
    active_shards_metric.set(active_shards)
    relocating_shards_metric.set(relocating_shards)
    number_of_nodes_metric.set(number_of_nodes)
    active_shards_percent_as_number_metric.set(active_shards_percent_as_number)

    # Update Prometheus metrics for each index
    for index_name, index_stats in indices_stats["indices"].items():
        index_documents_metric.labels(index=index_name).set(
            index_stats["total"]["docs"]["count"])
        index_size_bytes_metric.labels(index=index_name).set(
            index_stats["total"]["store"]["size_in_bytes"])
        index_search_query_total_metric.labels(index=index_name).set(
            index_stats["total"]["search"]["query_total"])
        index_search_query_time_seconds_metric.labels(index=index_name).set(
            index_stats["total"]["search"]["query_time_in_millis"] / 1000.0)

if __name__ == "__main__":
    # Start the Prometheus metrics HTTP server on port 8000
    start_http_server(8000)

    # Periodically update metrics (every 30 seconds in this example)
    while True:
        update_metrics()
        time.sleep(30)
