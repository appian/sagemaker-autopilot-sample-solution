import boto3
import json
from datetime import datetime

# Helper function to convert datetime to a string that JSON can serialize
def default_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()

# The Lambda function handler
def lambda_handler(event, context):
    # Initialize the SageMaker client
    sagemaker_client = boto3.client('sagemaker')

    # Extract the pipeline name from the event if passed
    pipeline_name = event.get('PipelineName', 'default-pipeline-name')  # Replace 'default-pipeline-name' with your pipeline name

    try:
        # Get the list of pipeline executions
        paginator = sagemaker_client.get_paginator('list_pipeline_executions')
        pipeline_executions = []

        for page in paginator.paginate(PipelineName=pipeline_name):
            pipeline_executions.extend(page['PipelineExecutionSummaries'])

        # Serialize the response using the custom converter for datetime objects
        response_json = json.dumps(pipeline_executions, default=default_converter)

        # Return the serialized executions list
        return {
            'statusCode': 200,
            'body': response_json
        }

    except Exception as e:
        # Return any error that occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# Replace the default handler with this updated one and redeploy the Lambda function
