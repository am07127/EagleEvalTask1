from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from openai import OpenAI
import boto3
import uuid
import os
from typing import Optional

app = FastAPI()


# Initialize OpenAI client with proper key handling
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=api_key)

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
TABLE_NAME = 'CsvSummaries'
TOPIC_ARN = 'arn:aws:sns:us-east-1:533267378744:CsvSummaryTopic'
table = dynamodb.Table(TABLE_NAME)

@app.post("/summarize")
async def summarize_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    # Read the file content
    df = pd.read_csv(file.file)

    # Create a prompt for the LLM
    prompt = f"Please summarize the following CSV data:\n\n{df.head(10).to_csv(index=False)}"

    try:
        client = get_openai_client()  # Get properly configured client
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        summary_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")

    # Store result in DynamoDB
    summary_id = str(uuid.uuid4())
    item = {
        "id": summary_id,
        "summary": summary_text,
        "filename": file.filename
    }

    try:
        table.put_item(Item=item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB error: {str(e)}")

    # Publish SNS event
    try:
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=f"New CSV summary created with ID: {summary_id}",
            Subject="CSV Summary Created"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SNS error: {str(e)}")

    return JSONResponse(content={"id": summary_id, "summary": summary_text})