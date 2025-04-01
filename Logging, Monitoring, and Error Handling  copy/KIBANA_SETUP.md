# Kibana Setup Guide

This document provides instructions for setting up and using Kibana as the primary visualization tool for the logging, monitoring, and error handling infrastructure.

## Overview

Kibana is a powerful visualization platform that allows you to explore, visualize, and analyze your data. This project includes scripts and configuration files to automate the setup and use of Kibana with the logging, monitoring, and error handling infrastructure.

## Environment Configuration

The `.env` file contains environment variables used by the scripts to connect to Kibana and Elasticsearch. It also includes browser configuration options to bypass security restrictions.

```
# Elastic Cloud credentials
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=8gwuBTOzZjmVMVqSMLqqtEcP

# Kibana URL
KIBANA_URL=https://aiif-logging.kb.us-east-2.aws.elastic-cloud.com:443

# Elasticsearch URL
ELASTICSEARCH_URL=https://aiif-logging.es.us-east-2.aws.elastic-cloud.com:443

# Browser configuration to bypass plugins and security policies
BROWSER_ARGS="--disable-web-security --disable-extensions --disable-plugins --no-sandbox --disable-popup-blocking --disable-notifications"
```

## Available Scripts

### 1. `run_kibana_infrastructure.sh`

This script starts the infrastructure with Kibana as the primary visualization tool. It starts the necessary services (Filebeat, Metricbeat, Prometheus, PostgreSQL) and opens Kibana in your browser.

```bash
./run_kibana_infrastructure.sh
```

### 2. `open_kibana.sh`

This script opens Kibana in your browser with security restrictions bypassed and automatically logs in using the credentials from the `.env` file.

```bash
./open_kibana.sh
```

### 3. `open_prometheus.sh`

This script opens Prometheus in your browser with security restrictions bypassed.

```bash
./open_prometheus.sh
```

### 4. `create_kibana_index_patterns.sh`

This script creates index patterns in Kibana using the Kibana API. It creates the following index patterns:
- `orchestrator-logs-*`
- `filebeat-*`
- `metricbeat-*`

```bash
./create_kibana_index_patterns.sh
```

### 5. `import_kibana_dashboards.sh`

This script imports sample dashboards into Kibana using the Kibana API. It imports the dashboards from the `kibana_sample_dashboards.ndjson` file.

```bash
./import_kibana_dashboards.sh
```

### 6. `run_all.sh`

This script runs the entire infrastructure, test agent, and visualization tools. It performs the following steps:
1. Starts the infrastructure with Kibana
2. Runs the test agent in the background
3. Creates Kibana index patterns
4. Imports Kibana dashboards
5. Opens Prometheus

```bash
./run_all.sh
```

## Sample Dashboards

The `kibana_sample_dashboards.ndjson` file contains sample dashboards that can be imported into Kibana. The following dashboards are included:

1. **Log Analysis Dashboard**
   - Log volume over time
   - Distribution of log severity
   - Top event types
   - Error logs table
   - Log volume by agent/service

2. **Metrics Dashboard**
   - Tasks dispatched over time
   - Errors by type
   - Task latency
   - Active tasks by agent type

3. **Operational Overview Dashboard**
   - Error rate
   - Task throughput
   - Log volume by severity
   - Recent error logs

## Troubleshooting

### Browser Security Issues

If you encounter browser security issues when accessing Kibana, try using the `open_kibana.sh` script which bypasses security restrictions.

### API Authentication Issues

If you encounter authentication issues when using the Kibana API, check the credentials in the `.env` file and ensure they are correct.

### Missing Index Patterns

If you don't see data in Kibana, check that the index patterns have been created correctly. You can create them manually through the Kibana UI or use the `create_kibana_index_patterns.sh` script.

### Missing Dashboards

If you don't see the sample dashboards in Kibana, check that they have been imported correctly. You can import them manually through the Kibana UI or use the `import_kibana_dashboards.sh` script.

## Additional Resources

For more detailed information on using Kibana, see the [KIBANA_VISUALIZATION_GUIDE.md](KIBANA_VISUALIZATION_GUIDE.md) file.
