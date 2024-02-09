import boto3
from datetime import datetime, timezone, timedelta

def time_ago(dt):
    now = datetime.now(timezone.utc)
    diff = now - dt

    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    if days > 0:
        if hours >= 12:
            days += 1
        return f"{days} days ago"
    elif hours > 0:
        if minutes >= 30:
            hours += 1
        return f"{hours} hours ago"
    elif minutes > 0:
        return f"{minutes} minutes ago"
    else:
        return "just now"

def list_sagemaker_resources(prefix, days_old, enable):
    sagemaker = boto3.client('sagemaker')
    endpoints = sagemaker.list_endpoints()['Endpoints']

    merged_data = []
    deletion_threshold = datetime.now(timezone.utc) - timedelta(days=days_old)
    deleted_endpoints = []

    for endpoint in endpoints:
        endpoint_name = endpoint['EndpointName']
        creation_time = endpoint['CreationTime']
        to_purge = creation_time < deletion_threshold

        # Apply prefix filtering only if prefix is provided and not empty
        if prefix and not endpoint_name.startswith(prefix):
            continue

        endpoint_info = {
            'endpoint_name': endpoint_name,
            'endpoint_status': endpoint['EndpointStatus'],
            'created': time_ago(creation_time),
            'to_purge': to_purge
        }
        merged_data.append(endpoint_info)

        if enable and to_purge:
            sagemaker.delete_endpoint(EndpointName=endpoint_name)
            deleted_endpoints.append(endpoint_name)

    return merged_data, deleted_endpoints

def lambda_handler(event, context):
    prefix = event.get('Prefix', '')
    days_old = int(event.get('DaysOld', 7))
    enable = event.get('Enable', False)  # Default to False if not provided

    resources_info, deleted_endpoints = list_sagemaker_resources(prefix, days_old, enable)
    return {
        'statusCode': 200,
        'body': {
            'endpoint_info': resources_info,
            'deleted_endpoints': deleted_endpoints if enable else "Deletion disabled"
        }
    }
