import os

from elasticsearch import Elasticsearch


# you can get an API_KEY from Kibana's managment section :)
elastic_api_key = "TU5iOGdJd0JERzEyZUhBUVFqOU86dTFUcDRQODVRNmFSYkxwdmJSdHhhZw=="


# Create the client instance
eclient = Elasticsearch(
    "https://es01:9200",
    ca_certs="/escerts/certs/ca/ca.crt",
    api_key=elastic_api_key
)

# create an index

resp = eclient.index(
    index="my_index",
    # id="my_document_id_1",
    document={
        "foo": "foo",
        "bar": "bar",
    }
)

print(resp)