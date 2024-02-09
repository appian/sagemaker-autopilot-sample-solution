import boto3
import json
from datetime import datetime

# Helper function to convert datetime to a string that JSON can serialize
def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()

# The Lambda function handler
def lambda_handler(event, context):
    # Create a SageMaker client using Boto3
    sagemaker = boto3.client('sagemaker')

    # Extract the endpoint name from the event
    if 'EndpointName' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'EndpointName not provided in the event'})
        }
    endpoint_name = event['EndpointName']

    try:
        # Describe the SageMaker endpoint
        endpoint_response = sagemaker.describe_endpoint(
            EndpointName=endpoint_name
        )

        # Serialize the response using the custom converter for datetime objects
        response_json = json.dumps(endpoint_response, default=datetime_converter)

        # Return the details of the endpoint
        return {
            'statusCode': 200,
            'body': response_json
        }

    except sagemaker.exceptions.ResourceNotFoundException:
        # Return a not found message if the endpoint does not exist
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Endpoint {endpoint_name} not found'})
        }
    except Exception as e:
        # Return any error that occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# Make sure to assign the proper permissions to your Lambda function's execution role
