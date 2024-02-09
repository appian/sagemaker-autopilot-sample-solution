import boto3
from datetime import datetime, timezone, timedelta
import re

def time_ago(dt):
    now = datetime.now(timezone.utc)
    diff = now - dt

    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    # Round up to the next unit if close to it
    if days > 0:
        if hours >= 12:  # Add one day if more than 12 hours
            days += 1
        return f"{days} days ago"
    elif hours > 0:
        if minutes >= 30:  # Add one hour if more than 30 minutes
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

def list_sagemaker_model_registry(prefix, pipeline_name):
    sagemaker = boto3.client('sagemaker')
    response = sagemaker.list_models(MaxResults=100)
    models = response.get('Models', [])

    latest_models = {}
    for model in models:
        model_name = model.get('ModelName')
        creation_time = model.get('CreationTime')
        formatted_model_name = format_model_name(model_name)

        if model_name.startswith(prefix) and pipeline_name not in formatted_model_name:
            if formatted_model_name not in latest_models or latest_models[formatted_model_name]['Raw Creation Time'] < creation_time:
                latest_models[formatted_model_name] = {
                    'ModelName': formatted_model_name,
                    'Raw Creation Time': creation_time,
                #    'Creation Time': creation_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'CreatedOn': time_ago(creation_time)
                }

    # Remove 'Raw Creation Time' from the output
    for model in latest_models.values():
        model.pop('Raw Creation Time', None)

    return list(latest_models.values())

def lambda_handler(event, context):
    prefix = event.get('Prefix', '')  
    pipeline_name = event.get('Pipeline_Name', '')  
    model_info_list = list_sagemaker_model_registry(prefix, pipeline_name)
    return {
        'statusCode': 200,
        'body': model_info_list
    }
