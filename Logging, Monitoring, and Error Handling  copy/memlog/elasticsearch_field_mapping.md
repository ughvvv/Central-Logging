# Elasticsearch Field Mapping in Grafana Dashboards

## Overview

This document explains how Elasticsearch maps fields and how to properly query them in Grafana dashboards.

## Background

When logs are sent to Elasticsearch, string fields are dynamically mapped as both:

1. A full-text searchable field (the field name itself)
2. A non-analyzed keyword field (the field name with a `.keyword` suffix)

For example, a field named `event_type` will be mapped as:
- `event_type`: Full-text searchable, tokenized, and analyzed
- `event_type.keyword`: Exact match, not analyzed, suitable for aggregations

## Issue

When creating Grafana dashboards that use Elasticsearch as a data source, you need to use the `.keyword` suffix for string fields when:

- Creating aggregations (like in pie charts, bar charts, etc.)
- Filtering on exact values
- Sorting by string fields

If you don't use the `.keyword` suffix, Grafana will try to aggregate on the analyzed field, which doesn't work well for aggregations and can result in "No data" being displayed.

## Solution

We updated the Test Agent Dashboard to use the `.keyword` suffix for the following fields:

- `event_type.keyword` instead of `event_type`
- `severity.keyword` instead of `severity`

This change allowed the Event Types and Log Severity panels to properly display data.

## Best Practices

When creating Grafana dashboards with Elasticsearch:

1. For aggregations (terms, filters, etc.), always use the `.keyword` suffix for string fields
2. For full-text search, use the field name without the suffix
3. For numeric and date fields, no suffix is needed

## Example

```json
{
  "bucketAggs": [
    {
      "field": "event_type.keyword",  // Use .keyword for aggregations
      "id": "2",
      "settings": {
        "min_doc_count": 1,
        "order": "desc",
        "orderBy": "_count",
        "size": "10"
      },
      "type": "terms"
    }
  ]
}
```

## Troubleshooting

If a panel in your Grafana dashboard shows "No data" when you expect it to show data:

1. Check if you're using string fields for aggregations
2. Add the `.keyword` suffix to those fields
3. Verify that the time range includes data
4. Check that the query filters aren't too restrictive

## References

- [Elasticsearch Field Datatypes](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html)
- [Elasticsearch Text vs Keyword](https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html#text-field-type)
- [Grafana Elasticsearch Query Editor](https://grafana.com/docs/grafana/latest/datasources/elasticsearch/)
