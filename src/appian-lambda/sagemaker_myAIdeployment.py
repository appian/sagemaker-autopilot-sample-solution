import boto3
from datetime import datetime, timezone, timedelta
import re

def time_ago(dt):
    # Calculate the time difference between now and the provided datetime
    now = datetime.now(timezone.utc)
    diff = now - dt

    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    # Format the time difference in a human-readable format
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
        
def format_model_name(model_name):
    match = re.match(r"(.*?)(-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})?$", model_name)
    if match:
        return match.group(1)
    return model_name

def list_sagemaker_model_registry(prefix):
    sagemaker = boto3.client('sagemaker')
    response = sagemaker.list_models(MaxResults=100)
    models = response.get('Models', [])
    endpoints = sagemaker.list_endpoints(NameContains=prefix)['Endpoints'] if prefix else sagemaker.list_endpoints()['Endpoints']
        
        # Prepare merged data
    merged_data = []
    latest_models = {}    

    latest_models = {}
    for model in models:
        model_name = model.get('ModelName')
        creation_time = model.get('CreationTime')
        formatted_model_name = format_model_name(model_name)

        if model_name.startswith(prefix):
            if formatted_model_name not in latest_models or latest_models[formatted_model_name]['Raw Creation Time'] < creation_time:
                latest_models[formatted_model_name] = {
                    'ModelName': formatted_model_name,
                    'Raw Creation Time': creation_time,
                }

    # Remove 'Raw Creation Time' from the output
    for model in latest_models.values():
        model.pop('Raw Creation Time', None)

    #return list(latest_models.values())
    
    # Iterate over the latest versions of models
    for model_name, model in latest_models.items():
        # Find all corresponding endpoints for the model
        matching_endpoints = [ep for ep in endpoints if ep['EndpointName'].startswith(model_name)]
    
        # Construct the rows for each matching endpoint
        for endpoint_match in matching_endpoints:
            endpoint_info = {
                'model_name': model_name,
                'endpoint_name': endpoint_match['EndpointName'],
                'endpoint_url': f"https://runtime.sagemaker.{boto3.Session().region_name}.amazonaws.com/endpoints/{endpoint_match['EndpointName']}/invocations",
                'endpoint_status': endpoint_match['EndpointStatus'],
                'created': time_ago(endpoint_match['CreationTime'])
            }
            merged_data.append(endpoint_info)

    return merged_data

def lambda_handler(event, context):
    prefix = event.get('Prefix', '')  
    model_info_list = list_sagemaker_model_registry(prefix)
    return {
        'statusCode': 200,
        'body': model_info_list
    }
