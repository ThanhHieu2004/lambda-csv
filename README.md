# Lambda CSV Processing Pipeline

A serverless application built with AWS SAM and Python 3.12 for uploading and processing supplier master CSV files.

---

## Architecture Overview

* **ApiFunction ([`api/app.py`](api/app.py))**:
  * `POST /uploads/presign`: Generates an S3 Presigned URL for direct client-side CSV upload.
  * `GET /jobs/{jobId}`: Retrieves the status of a CSV processing job from DynamoDB.
* **SupplierMasterBucket (Amazon S3)**:
  * Secure S3 bucket where clients upload CSV files to `input/*.csv`.
* **CsvProcessorFunction ([`processor/app.py`](processor/app.py))**:
  * Triggered automatically upon `s3:ObjectCreated:*` events under `input/*.csv`.
  * Parses CSV content and records job execution status.
* **JobTable (Amazon DynamoDB)**:
  * Tracks job status and metadata keyed by `jobId`.

---

## Prerequisites

Before running the application locally, make sure you have installed:

1. **Python 3.12+**: Required runtime for lambda functions and local testing.
2. **AWS SAM CLI**: Command line interface for building and testing SAM applications.
3. **Docker**: Required by AWS SAM to simulate Lambda execution environments locally.
4. **AWS CLI**: Useful for managing local credentials and AWS resources.

---

## Environment Configuration

The application relies on configuration parameters for AWS region, resource names, presigned URL expiration, and logging.

### 1. File Templates

The repository provides two template files for environment configuration:

* `.env.example`: Shell/Python environment variable template.
* `env.example.json`: AWS SAM CLI local execution parameter template.

Both files are tracked in version control, while `.env` and `env.json` are excluded in `.gitignore`.

### 2. Configure `.env`

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

Contents of `.env`:

```ini
# AWS Environment
AWS_REGION=ap-southeast-1
AWS_DEFAULT_REGION=ap-southeast-1

# Application Resources
BUCKET_NAME=your-bucket-name-here
JOB_TABLE_NAME=your-dynamodb-table-name-here

# Configurations
EXPIRY_MINUTES=15
LOG_LEVEL=INFO
```

### 3. Configure `env.json` for SAM CLI

For local emulation with AWS SAM (`sam local start-api` or `sam local invoke`), create `env.json` from `env.example.json`:

```bash
cp env.example.json env.json
```

Contents of `env.json`:

```json
{
  "ApiFunction": {
    "BUCKET_NAME": "your-bucket-name-here",
    "JOB_TABLE_NAME": "your-job-table-here",
    "EXPIRY_MINUTES": "15",
    "LOG_LEVEL": "INFO"
  },
  "CsvProcessorFunction": {
    "BUCKET_NAME": "your-bucket-name-here",
    "JOB_TABLE_NAME": "your-job-table-here",
    "LOG_LEVEL": "INFO"
  }
}
```

> **Security Notice**: Never commit `.env`, `env.json`, or real AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) to git. Both files are ignored in `.gitignore`.

---

## Local Setup and Execution

### Step 1: Create and Activate Virtual Environment

```bash
# Create virtual environment
python3.12 -m venv .venv

# Activate virtual environment
# On Linux / macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install editable project with dev dependencies
pip install -e ".[dev]"
```

Alternatively, you can install dependencies directly from the requirement files:

```bash
pip install -r api/requirements.txt -r processor/requirements.txt -r tests/requirements.txt
```

---

### Step 2: Build the Application

Build the application using AWS SAM CLI:

```bash
sam build
```

SAM packages all dependencies for both `ApiFunction` and `CsvProcessorFunction` into the `.aws-sam` build directory.

---

### Step 3: Run Local API Gateway

Start the local API Gateway emulator using Docker:

```bash
sam local start-api --env-vars env.json
```

By default, the server starts at `http://127.0.0.1:3000`.

#### Test API Endpoints

1. **Request Presigned Upload URL**:

```bash
curl -X POST http://127.0.0.1:3000/uploads/presign \
  -H "Content-Type: application/json" \
  -d '{"filename": "supplier_data.csv"}'
```

2. **Check Job Status**:

```bash
curl -X GET http://127.0.0.1:3000/jobs/test-job-id-123
```

---

### Step 4: Invoke Functions Directly

You can invoke individual Lambda functions directly without running the API server.

#### Invoke `ApiFunction`

```bash
sam local invoke ApiFunction --env-vars env.json -e events/event.json
```

#### Invoke `CsvProcessorFunction`

To test the S3-triggered processor, generate a mock S3 event:

```bash
# Generate S3 put notification event
sam local generate-event s3 put \
  --bucket supplier-master-bucket \
  --key input/sample.csv > events/s3_event.json

# Invoke processor function
sam local invoke CsvProcessorFunction --env-vars env.json -e events/s3_event.json
```

---

## Testing

Run tests with `pytest`:

```bash
# Run test suite
pytest

# If running without editable install
PYTHONPATH=. pytest
```

Test structure:
* `tests/unit/`: Unit tests for Lambda handlers and helper logic.
* `tests/integration/`: Integration tests for API Gateway and service flows.

---

## Project Structure

```text
lambda-csv/
├── .env.example                  # Environment variable template
├── .env                          # Local environment variables (git-ignored)
├── env.example.json              # SAM local environment parameters template
├── env.json                      # SAM local environment parameters (git-ignored)
├── .gitignore                    # Git ignore file
├── README.md                     # Documentation
├── pyproject.toml                # Build configuration and dependency definitions
├── samconfig.toml                # AWS SAM CLI default configurations
├── template.yaml                 # SAM CloudFormation template
├── api/                          # ApiFunction source code
│   ├── app.py                    # API Lambda handler
│   └── requirements.txt          # API dependencies
├── processor/                    # CsvProcessorFunction source code
│   ├── app.py                    # S3 CSV processor handler
│   └── requirements.txt          # Processor dependencies
├── events/                       # Mock event payloads for local invocations
│   └── event.json
└── tests/                        # Automated test suites
    ├── requirements.txt          # Test dependencies
    ├── unit/                     # Unit tests
    └── integration/              # Integration tests
```
