#!/usr/bin/env python3
"""
CSV/Excel Processor
Process, transform, and analyze CSV/Excel data
"""

import json
import logging
import io
import csv
import base64
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_csv(csv_data, has_header=True, delimiter=','):
    """
    Parse CSV data
    
    Args:
        csv_data: CSV string or base64 encoded data
        has_header: Whether first row is header
        delimiter: CSV delimiter
    
    Returns:
        dict: Parsed data with headers and rows
    """
    # Handle base64 encoded data
    try:
        csv_string = base64.b64decode(csv_data).decode('utf-8')
    except:
        csv_string = csv_data
    
    # Parse CSV
    reader = csv.reader(io.StringIO(csv_string), delimiter=delimiter)
    rows = list(reader)
    
    if not rows:
        return {'headers': [], 'data': [], 'row_count': 0}
    
    if has_header:
        headers = rows[0]
        data_rows = rows[1:]
    else:
        headers = [f'col_{i}' for i in range(len(rows[0]))]
        data_rows = rows
    
    # Convert to list of dicts
    data = []
    for row in data_rows:
        row_dict = {}
        for i, value in enumerate(row):
            if i < len(headers):
                row_dict[headers[i]] = value
        data.append(row_dict)
    
    return {
        'headers': headers,
        'data': data,
        'row_count': len(data),
        'column_count': len(headers)
    }


def generate_csv(data, headers=None, delimiter=','):
    """
    Generate CSV from data
    
    Args:
        data: List of dictionaries or list of lists
        headers: Optional custom headers
        delimiter: CSV delimiter
    
    Returns:
        str: CSV string
    """
    output = io.StringIO()
    
    if not data:
        return ''
    
    # Handle list of dicts
    if isinstance(data[0], dict):
        if headers is None:
            headers = list(data[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=headers, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)
    
    # Handle list of lists
    else:
        writer = csv.writer(output, delimiter=delimiter)
        if headers:
            writer.writerow(headers)
        writer.writerows(data)
    
    return output.getvalue()


def filter_rows(data, filters):
    """
    Filter rows based on conditions
    
    Args:
        data: List of dictionaries
        filters: Dict of column: value pairs
    
    Returns:
        list: Filtered rows
    """
    filtered = []
    for row in data:
        match = True
        for col, value in filters.items():
            if col not in row or str(row[col]) != str(value):
                match = False
                break
        if match:
            filtered.append(row)
    
    return filtered


def aggregate_data(data, group_by, aggregate_col, operation='sum'):
    """
    Aggregate data
    
    Args:
        data: List of dictionaries
        group_by: Column to group by
        aggregate_col: Column to aggregate
        operation: Aggregation operation (sum, avg, count, min, max)
    
    Returns:
        list: Aggregated results
    """
    groups = defaultdict(list)
    
    # Group data
    for row in data:
        key = row.get(group_by, 'N/A')
        value = row.get(aggregate_col, 0)
        
        # Try to convert to number
        try:
            value = float(value)
        except:
            value = 0
        
        groups[key].append(value)
    
    # Aggregate
    results = []
    for key, values in groups.items():
        if operation == 'sum':
            result = sum(values)
        elif operation == 'avg':
            result = sum(values) / len(values) if values else 0
        elif operation == 'count':
            result = len(values)
        elif operation == 'min':
            result = min(values) if values else 0
        elif operation == 'max':
            result = max(values) if values else 0
        else:
            result = 0
        
        results.append({
            group_by: key,
            f'{operation}_{aggregate_col}': result,
            'count': len(values)
        })
    
    return results


def sort_data(data, sort_by, reverse=False):
    """
    Sort data by column
    
    Args:
        data: List of dictionaries
        sort_by: Column to sort by
        reverse: Sort in descending order
    
    Returns:
        list: Sorted data
    """
    def get_sort_key(row):
        value = row.get(sort_by, '')
        try:
            return float(value)
        except:
            return str(value)
    
    return sorted(data, key=get_sort_key, reverse=reverse)


def get_statistics(data, column):
    """
    Get statistics for a numeric column
    
    Args:
        data: List of dictionaries
        column: Column name
    
    Returns:
        dict: Statistics
    """
    values = []
    for row in data:
        try:
            values.append(float(row.get(column, 0)))
        except:
            pass
    
    if not values:
        return {
            'count': 0,
            'sum': 0,
            'mean': 0,
            'min': 0,
            'max': 0
        }
    
    return {
        'count': len(values),
        'sum': sum(values),
        'mean': sum(values) / len(values),
        'min': min(values),
        'max': max(values)
    }


def handle(event, context):
    """
    OpenFaaS handler for CSV processing
    
    Request body for parsing:
    {
        "operation": "parse",
        "data": "csv_string_or_base64",
        "has_header": true,
        "delimiter": ","
    }
    
    Request body for generation:
    {
        "operation": "generate",
        "data": [{"col1": "val1", "col2": "val2"}, ...],
        "headers": ["col1", "col2"],  # optional
        "delimiter": ","  # optional
    }
    
    Request body for filtering:
    {
        "operation": "filter",
        "data": [{"col1": "val1", "col2": "val2"}, ...],
        "filters": {"col1": "val1"}
    }
    
    Request body for aggregation:
    {
        "operation": "aggregate",
        "data": [{"category": "A", "value": 10}, ...],
        "group_by": "category",
        "aggregate_col": "value",
        "aggregate_op": "sum"  # sum, avg, count, min, max
    }
    
    Request body for sorting:
    {
        "operation": "sort",
        "data": [{"col1": "val1", "col2": "val2"}, ...],
        "sort_by": "col1",
        "reverse": false
    }
    
    Request body for statistics:
    {
        "operation": "statistics",
        "data": [{"value": 10}, {"value": 20}, ...],
        "column": "value"
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received CSV processing request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'parse')
        data = payload.get('data')
        
        if data is None:
            return {
                "statusCode": 400,
                "body": {"error": "Missing 'data' field"},
                "headers": {"Content-Type": "application/json"}
            }
        
        if operation == 'parse':
            has_header = payload.get('has_header', True)
            delimiter = payload.get('delimiter', ',')
            
            logger.info("Parsing CSV data...")
            result = parse_csv(data, has_header, delimiter)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "message": "CSV parsed successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'generate':
            headers = payload.get('headers')
            delimiter = payload.get('delimiter', ',')
            
            logger.info("Generating CSV...")
            csv_string = generate_csv(data, headers, delimiter)
            
            return {
                "statusCode": 200,
                "body": {
                    "csv": csv_string,
                    "row_count": len(data),
                    "message": "CSV generated successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'filter':
            filters = payload.get('filters', {})
            
            logger.info("Filtering data...")
            filtered = filter_rows(data, filters)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": filtered,
                    "original_count": len(data),
                    "filtered_count": len(filtered),
                    "message": "Data filtered successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'aggregate':
            group_by = payload.get('group_by')
            aggregate_col = payload.get('aggregate_col')
            aggregate_op = payload.get('aggregate_op', 'sum')
            
            if not group_by or not aggregate_col:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'group_by' or 'aggregate_col'"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Aggregating data...")
            result = aggregate_data(data, group_by, aggregate_col, aggregate_op)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "group_count": len(result),
                    "message": "Data aggregated successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'sort':
            sort_by = payload.get('sort_by')
            reverse = payload.get('reverse', False)
            
            if not sort_by:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'sort_by'"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Sorting data...")
            sorted_data = sort_data(data, sort_by, reverse)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": sorted_data,
                    "row_count": len(sorted_data),
                    "message": "Data sorted successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'statistics':
            column = payload.get('column')
            
            if not column:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'column'"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Calculating statistics...")
            stats = get_statistics(data, column)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": stats,
                    "column": column,
                    "message": "Statistics calculated successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        else:
            return {
                "statusCode": 400,
                "body": {"error": f"Unknown operation: {operation}"},
                "headers": {"Content-Type": "application/json"}
            }
    
    except Exception as e:
        logger.error(f"Error in CSV processing: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
