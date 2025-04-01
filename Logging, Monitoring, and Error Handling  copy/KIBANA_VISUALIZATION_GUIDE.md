# Kibana Visualization Guide

This document provides guidance on using Kibana as the primary visualization tool for the logging, monitoring, and error handling infrastructure.

## Overview

Kibana is a powerful visualization platform that allows you to explore, visualize, and analyze your data. It provides a wide range of visualization types, dashboards, and analytics capabilities. This guide will help you set up and use Kibana effectively with this project.

## Accessing Kibana

Kibana is hosted on Elastic Cloud and can be accessed at:

- **URL**: https://aiif-logging.kb.us-east-2.aws.elastic-cloud.com:443
- **Username**: elastic
- **Password**: 8gwuBTOzZjmVMVqSMLqqtEcP

## Setting Up Index Patterns

Before you can visualize your data, you need to set up index patterns in Kibana. Index patterns tell Kibana which Elasticsearch indices you want to explore.

1. In Kibana, go to **Stack Management** > **Index Patterns**
2. Click **Create index pattern**
3. Create the following index patterns:
   - `orchestrator-logs-*` for orchestrator logs
   - `filebeat-*` for general logs
   - `metricbeat-*` for metrics (after running with Metricbeat)
4. For each index pattern, select `@timestamp` as the time field
5. Click **Create index pattern**

## Exploring Data

### Discover

The Discover page allows you to explore your data and perform ad-hoc searches:

1. Go to **Discover** in the main menu
2. Select the index pattern you want to explore
3. Use the time picker to select a time range
4. Use the search bar to filter your data (using KQL or Lucene query syntax)
5. Click on fields in the left sidebar to add them to the table view

### Key Queries for Troubleshooting

Here are some useful queries for troubleshooting:

- Find error logs: `severity:ERROR`
- Find logs from a specific agent: `agent_name:"orchestrator"`
- Find specific event types: `event_type:"task_dispatch"`
- Find logs with specific metadata: `metadata.task_id:"abc123"`

## Creating Visualizations

Kibana offers several ways to create visualizations:

### Lens (Recommended for Beginners)

Lens is a drag-and-drop interface for creating visualizations:

1. Go to **Visualize Library** in the main menu
2. Click **Create new visualization**
3. Select **Lens**
4. Drag fields from the left sidebar to the visualization builder
5. Choose visualization type from the top dropdown
6. Configure options in the right sidebar
7. Click **Save** when done

### Visualization Types for Logs

For log data, consider these visualization types:

1. **Data Table**: For detailed log analysis
2. **Line Chart**: For log volume over time
3. **Pie Chart**: For distribution of log severity or event types
4. **Bar Chart**: For comparing log counts by agent or service
5. **Heat Map**: For identifying patterns in log occurrence

### Visualization Types for Metrics

For metric data, consider these visualization types:

1. **Line Chart**: For time-series metrics
2. **Gauge**: For current values against thresholds
3. **Bar Chart**: For comparing metrics across services
4. **Area Chart**: For stacked metrics over time
5. **TSVB**: For advanced time-series visualizations

## Creating Dashboards

Dashboards allow you to combine multiple visualizations:

1. Go to **Dashboard** in the main menu
2. Click **Create dashboard**
3. Click **Add** to add visualizations
4. Select existing visualizations or create new ones
5. Arrange visualizations by dragging them
6. Resize visualizations as needed
7. Click **Save** when done

## Sample Dashboards

This project includes sample dashboards that you can import into Kibana:

### Importing Sample Dashboards

1. In Kibana, go to **Stack Management** > **Saved Objects**
2. Click **Import**
3. Select the `kibana_sample_dashboards.ndjson` file
4. Click **Import**
5. Resolve any conflicts if prompted (usually by selecting "Overwrite all")

### Available Sample Dashboards

The following sample dashboards are included:

#### Log Analysis Dashboard

- Log volume over time
- Distribution of log severity
- Top event types
- Error logs table
- Log volume by agent/service

#### Metrics Dashboard

- Tasks dispatched over time
- Errors by type
- Task latency
- Active tasks by agent type

#### Operational Overview Dashboard

- Error rate
- Task throughput
- Log volume by severity
- Recent error logs

### Creating Custom Dashboards

You can also create your own custom dashboards:

1. Go to **Dashboard** in the main menu
2. Click **Create dashboard**
3. Click **Add** to add visualizations
4. Select existing visualizations or create new ones
5. Arrange visualizations by dragging them
6. Resize visualizations as needed
7. Click **Save** when done

## Setting Up Alerts

Kibana allows you to set up alerts based on your data:

1. Go to **Stack Management** > **Rules and Connectors**
2. Click **Create rule**
3. Select a rule type (e.g., Threshold, Anomaly)
4. Configure the rule conditions
5. Set up actions (e.g., email, Slack)
6. Click **Save** when done

### Alert Examples

Consider setting up these alerts:

- High error rate alert
- System resource threshold alerts
- Service availability alerts
- Anomaly detection alerts for unusual patterns

## Advanced Features

### Canvas

Canvas allows you to create presentation-ready visualizations:

1. Go to **Canvas** in the main menu
2. Create a new workpad
3. Add elements from the toolbar
4. Connect elements to your data
5. Style and arrange elements
6. Present in fullscreen mode

### Maps

For geospatial data, Kibana Maps provides powerful visualization:

1. Go to **Maps** in the main menu
2. Create a new map
3. Add layers from your Elasticsearch data
4. Configure styling and tooltips
5. Save and add to dashboards

## Troubleshooting

If you encounter issues with Kibana:

1. Check that your index patterns are correctly configured
2. Verify that data is being sent to Elasticsearch
3. Check for mapping issues in Elasticsearch
4. Ensure your time range includes data
5. Check for query syntax errors

## Running the Infrastructure

To run the infrastructure with Kibana as the primary visualization tool:

```bash
./run_kibana_infrastructure.sh
```

This script will:
1. Start the necessary services (Filebeat, Metricbeat, Prometheus, PostgreSQL)
2. Open Kibana in your default browser
3. Provide instructions for next steps

## Generating Test Data

To generate test data for visualization:

```bash
./run_test_agent.sh
```

This will create sample logs and metrics that you can visualize in Kibana.
