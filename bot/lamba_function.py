import boto3
import json

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("chat_history")

# Lambda handler
def handler(event, context):
    user_id = event["user_id"]
    message = event["message"]
    response = event["response"]

    # Save to DynamoDB
    table.put_item(
        Item={
            "user_id": user_id,
            "message": message,
            "response": response
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps("Data saved successfully")
    }
