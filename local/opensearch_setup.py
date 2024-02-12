import os
import json
import time
import logging

import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter, Retry

logging.basicConfig(level=logging.INFO)


ENDPOINT = "https://localhost:9200"
INDEX_SPEC_PATH = os.path.join(
    os.path.dirname(__file__), "index_spec.json",
)
IS_LOCAL = os.getenv("IS_LOCAL", "false").lower() == "true"

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
session.mount('https://', HTTPAdapter(max_retries=retries))

if IS_LOCAL:
    request_settings = {
        "auth": HTTPBasicAuth('admin', 'admin'),
        "verify": False,
        "timeout": 5,
    }
else:
    request_settings = {
        "verify": False,
        "timeout": 10,
    }

def setup_cluster():
    index_name = "anime_v1"
    alias_name = "anime"
    ingest_pipeline_name = "embeddings-pipeline"
    search_pipeline_name = "search-embeddings-pipeline"
    field_embeddings = "synopsis"

    set_cluster_settings()

    model_id = setup_embeddings_model()
    print(create_ingest_pipeline(ingest_pipeline_name, model_id, field_embeddings))
    print(create_index(index_name, ingest_pipeline_name))
    print(create_alias(index_name, alias_name))
    print(create_search_pipeline(search_pipeline_name, model_id))
    print(set_index_search_pipeline(alias_name, search_pipeline_name))

def set_cluster_settings() -> dict:
    logging.info("Setting ML settings in cluster...")
    url = f"{ENDPOINT}/_cluster/settings"
    ml_settings = {
        "persistent": {
            "plugins.ml_commons.only_run_on_ml_node": False,
            "plugins.ml_commons.model_access_control_enabled": True,
            "plugins.ml_commons.native_memory_threshold": 99,
        }
    }
    response = session.put(url=url, json=ml_settings, **request_settings)
    return response.json()


def setup_embeddings_model() -> str:
    model_group_id = create_model_group()

    registration_task_id = register_model(model_group_id)
    model_id = wait_for_task_completion(registration_task_id)["model_id"]

    deployment_task_id = deploy_model(model_id)
    wait_for_task_completion(deployment_task_id)

    return model_id

def create_model_group() -> str:
    logging.info("Creating model group...")
    url = f"{ENDPOINT}/_plugins/_ml/model_groups/_register"
    payload = {
        "name": "embeddings_model_group",
        "description": "A model group for embeddings"
    }
    response = session.post(url, json=payload, **request_settings)
    print(response.json())
    return response.json()["model_group_id"]

def register_model(model_group_id: str) -> str:
    logging.info(f"Registering model in model_group {model_group_id}...")
    url = f"{ENDPOINT}/_plugins/_ml/models/_register"
    payload = {
        "name": "huggingface/sentence-transformers/all-mpnet-base-v2",
        "version": "1.0.1",
        "model_group_id": model_group_id,
        "model_format": "TORCH_SCRIPT"
    }
    response = session.post(url, json=payload, **request_settings)
    return response.json()["task_id"]

def wait_for_task_completion(task_id: str) -> dict[str, str]:
    logging.info(f"Awaiting completion of task {task_id}...")
    url = f"{ENDPOINT}/_plugins/_ml/tasks/{task_id}"
    print(f"URl: {url}")
    response = session.get(url, **request_settings)
    response_json = response.json()

    print(response_json)

    while (response_json["state"] != "COMPLETED"):
        time.sleep(10)
        response_json = wait_for_task_completion(task_id)
        print(response_json)

    return response_json 


def deploy_model(model_id: str):
    logging.info(f"Deploying model {model_id}...")
    url = f"{ENDPOINT}/_plugins/_ml/models/{model_id}/_deploy"
    response = session.post(url, **request_settings)
    return response.json()["task_id"]

def create_ingest_pipeline(pipeline_name: str, model_id: str, field_name: str) -> dict:
    logging.info(f"Creating ingest pipeline {pipeline_name} with model {model_id}...")
    url = f"{ENDPOINT}/_ingest/pipeline/{pipeline_name}"
    payload = {
        "description": "Embeddings ingest pipeline",
        "processors": [
            {
                "text_embedding": {
                    "model_id": model_id,
                    "field_map": {
                        field_name: f"{field_name}_embedding"
                    }
                }
            }
        ]
    }
    response = session.put(url, json=payload, **request_settings)
    return response.json()

def create_index(index_name: str, ingest_pipeline_name: str):
    logging.info(f"Creating index {index_name} with ingest pipeline {ingest_pipeline_name}...")
    url = f"{ENDPOINT}/{index_name}"
    index_spec = retrieve_index_spec()
    index_spec["settings"]["default_pipeline"] = ingest_pipeline_name

    response = session.put(url, json=index_spec, **request_settings)
    return response.json()

def retrieve_index_spec():
    logging.info(f"Retrieving index specification from file {INDEX_SPEC_PATH}...")
    with open(INDEX_SPEC_PATH, "r") as f:
        return json.loads(f.read())

def create_search_pipeline(pipeline_name: str, model_id: str) -> dict:
    logging.info("Creating search pipeline...")
    url = f"{ENDPOINT}/_search/pipeline/{pipeline_name}"
    payload = {
      "request_processors": [
        {
          "neural_query_enricher" : {
            "neural_field_default_id": {
               "synopsis_embedding": model_id,
            }
          }
        }
      ]
    }
    response = session.put(url, json=payload, **request_settings)

    return response.json()

def set_index_search_pipeline(index_name: str, pipeline_name: str) -> dict:
    logging.info("Assigning search pipeline to index...")
    url = f"{ENDPOINT}/{index_name}/_settings"
    payload = {
      "index.search.default_pipeline" : pipeline_name
    }
    response = session.put(url, json=payload, **request_settings)
    return response.json()

def create_alias(index_name: str, alias_name: str) -> dict:
    logging.info(f"Creating alias {alias_name} for index {index_name}...")
    url = f"{ENDPOINT}/_aliases"
    payload = {
        "actions": [
            {"add": {"index": index_name, "alias": alias_name}}
        ]
    }
    response = session.post(url, json=payload, **request_settings)
    return response.json()

if __name__ == "__main__":
    setup_cluster()
