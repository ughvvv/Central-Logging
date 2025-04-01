# Elastic Cloud Integration

This document explains how to use the logging, monitoring, and error handling infrastructure with Elastic Cloud instead of the local Elasticsearch and Kibana containers.

## Overview

The infrastructure has been updated to support sending logs to Elastic Cloud instead of the local Elasticsearch container. This allows you to leverage Elastic Cloud's managed services for log storage, visualization, and analysis.

## Configuration Files

The following files have been created or modified to support Elastic Cloud:

1. **filebeat.yml**: Updated to send logs to Elastic Cloud Elasticsearch
2. **docker-compose.cloud.yml**: Modified version of docker-compose.yml that removes the local Elasticsearch and Kibana services
3. **grafana/provisioning/datasources/elasticsearch.yml**: New datasource configuration for Grafana to connect to Elastic Cloud Elasticsearch
4. **validate_cloud_infrastructure.py**: Modified version of validate_infrastructure.py that checks Elastic Cloud endpoints
5. **run_cloud_infrastructure.sh**: Script to run the infrastructure with Elastic Cloud

## Elastic Cloud Credentials

The following Elastic Cloud credentials are used:

- **Username**: elastic
- **Password**: 8gwuBTOzZjmVMVqSMLqqtEcP

## Elastic Cloud Endpoints

The following Elastic Cloud endpoints are used:

- **Elasticsearch**: https://aiif-logging.es.us-east-2.aws.elastic-cloud.com:443
- **Kibana**: https://aiif-logging.kb.us-east-2.aws.elastic-cloud.com:443
- **Fleet**: https://aiif-logging.fleet.us-east-2.aws.elastic-cloud.com:443

## Running with Elastic Cloud

To run the infrastructure with Elastic Cloud, use the following command:

```bash
./run_cloud_infrastructure.sh
```

This script will:

1. Start the local services (Filebeat, Prometheus, Grafana, PostgreSQL)
2. Run the validation script to test the infrastructure
3. Run the test agent to generate logs and metrics
4. Provide instructions for checking the results

## Accessing Kibana

You can access Kibana at https://aiif-logging.kb.us-east-2.aws.elastic-cloud.com:443 using the following credentials:

- **Username**: elastic
- **Password**: 8gwuBTOzZjmVMVqSMLqqtEcP

## Accessing Grafana

You can access Grafana at http://localhost:3000 using the following credentials:

- **Username**: admin
- **Password**: admin

Grafana has been configured with an Elasticsearch datasource that connects to Elastic Cloud Elasticsearch.

## Troubleshooting

If you encounter any issues with the Elastic Cloud integration, check the following:

1. Verify that Filebeat is running and sending logs to Elastic Cloud
2. Check the Filebeat logs for any errors
3. Verify that the Elastic Cloud credentials are correct
4. Check that the Elastic Cloud endpoints are accessible
5. Verify that the Grafana Elasticsearch datasource is configured correctly
