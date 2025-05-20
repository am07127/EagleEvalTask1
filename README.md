# CSV Summarization API with FastAPI

This application provides an API endpoint that accepts CSV files, generates AI-powered summaries using OpenAI, stores results in DynamoDB, and publishes notifications via SNS.

## Prerequisites

- Python 3.9+
- AWS Account
- OpenAI API Key
- AWS CLI

## Setup Instructions

### 1. Clone the Repository
```bash
git https://github.com/am07127/EagleEvalTask1
```

### 2.  Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
OPENAI_API_KEY=your_openai_api_key_here
AWS_REGION=us-east-1
```

### 5. Configure your AWS Credentials using AWS CLI


### 6. Run the app

```bash
uvicorn main:app --reload
```



