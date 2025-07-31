# Scripts Directory

This directory contains utility scripts for deployment and testing of the Customer Insights GenAI API.

## Scripts Overview

### `deploy_lambda.py`
**Purpose**: Deploy and update Lambda function code

**Usage**:
```bash
# Direct lambda update (for development)
python scripts/deploy_lambda.py

# S3-based deployment (for CloudFormation)
python scripts/deploy_lambda.py --s3 --keep-zip

# Package only (no deployment)
python scripts/deploy_lambda.py --package-only
```

**Features**:
- Creates deployment package from `src/genai/` files
- Fixes relative imports automatically
- Supports both direct and S3-based deployment
- Handles function creation and updates
- Tests API endpoint after deployment

### `test_bedrock_api.py`
**Purpose**: Test the Customer Insights GenAI API with various scenarios

### `test_sagemaker_endpoint.py`
**Purpose**: Test the SageMaker K-means customer segmentation endpoint

**Usage**:
```bash
# Get API URL and test
API_URL=$(make get-api-url)

# Test different scenarios
python scripts/test_bedrock_api.py --api-url $API_URL --test-case product_feedback
python scripts/test_bedrock_api.py --api-url $API_URL --test-case safety_concern
python scripts/test_bedrock_api.py --api-url $API_URL --test-case spanish_feedback
python scripts/test_bedrock_api.py --api-url $API_URL --test-case positive_review
```

**Test Cases**:
- `product_feedback` - Mixed sentiment with setup issues
- `safety_concern` - Burn hazard detection (adverse events)
- `spanish_feedback` - Multi-language support testing
- `positive_review` - Positive sentiment analysis

**Output**:
- Response time measurement
- Sentiment analysis results
- Unmet needs and pain points
- Safety concerns detection
- Recommendations generated

**Usage**:
```bash
# List available SageMaker endpoints
python scripts/test_sagemaker_endpoint.py --list-endpoints

# Test specific endpoint
python scripts/test_sagemaker_endpoint.py --endpoint-name kmeans-2025-07-31-19-58-36-067
```

**Features**:
- Tests K-means clustering with normalized customer data
- Shows cluster assignments and distances to centroids
- Interprets customer segments with business-friendly names
- Validates endpoint performance and accuracy

## Integration with Makefile

These scripts are integrated with the project's Makefile:

```bash
make update-lambda     # Uses deploy_lambda.py
make test-api          # Uses curl (simple GenAI test)
make test-sagemaker    # Uses test_sagemaker_endpoint.py
make get-endpoints     # List SageMaker endpoints
```

For advanced testing, use the scripts directly as shown above.

## Performance Testing Results

### GenAI API Results:
- **Average Response Time**: 1.7s - 2.7s
- **Confidence Score**: 90%
- **Safety Detection**: Working (burn hazards detected)
- **Multi-language**: Spanish processing successful
- **Cost**: < $0.005 per request

### SageMaker Endpoint Results:
- **Inference Latency**: ~150ms average
- **Cluster Separation**: Average distance 1.081
- **Model Accuracy**: 5 clusters with good separation
- **Endpoint Status**: InService
- **Cost**: ~$0.10/hour when running

## Development Workflow

1. **Code Changes**: Modify files in `src/genai/`
2. **Deploy**: `python scripts/deploy_lambda.py --s3 --keep-zip`
3. **Test**: `python scripts/test_bedrock_api.py --api-url $API_URL --test-case safety_concern`
4. **Verify**: Check response times and accuracy

These scripts enable rapid development and testing of the GenAI functionality.