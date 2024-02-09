import json
import boto3

def delete_sagemaker_endpoint(endpoint_name):
    """
    Deletes a specified SageMaker endpoint.

    :param endpoint_name: Name of the SageMaker endpoint to delete.
    """
    # Create a SageMaker client
    sagemaker_client = boto3.client('sagemaker')

    # Delete the SageMaker endpoint
    response = sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
    
    return response

def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    :param event: The event dict that contains the input parameters.
    :param context: The context in which the Lambda function is called.
    """
    try:
        # Parse the EndpointName from the event
        endpoint_name = event['EndpointName']

        # Call the function to delete the SageMaker endpoint
        response = delete_sagemaker_endpoint(endpoint_name)

        return {
            'statusCode': 200,
            'body': json.dumps('Endpoint deleted successfully')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

# Example invocation (in Lambda test event format):
# {
#     "EndpointName": "my-endpoint-name"
# }
