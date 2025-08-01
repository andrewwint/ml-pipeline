# SageMaker Notebook Environment

This directory contains the SageMaker notebook for K-means customer segmentation model development.

## Notebook Overview

### `CustomerSegmentation.ipynb`

- **Purpose**: Complete K-means clustering pipeline from EDA to deployment
- **Algorithm**: K-means with 5 optimal clusters (silhouette score: 0.62)
- **Deployment**: Creates live SageMaker endpoint for real-time inference
- **Performance**: ~150ms inference latency

## SageMaker Infrastructure

### Instance Types

- **Notebook Instance**: `ml.t3.medium` - Cost-effective for development
- **Endpoint Instance**: `ml.m5.large` - Optimized for real-time inference

### Automated Lifecycle Configuration

The `NotebookInstanceLifecycleConfig` in CloudFormation handles:

1. **Environment Setup**

   - Configures S3 bucket environment variables
   - Sets up system-wide access to data and model buckets

2. **Git Integration**

   - Retrieves GitHub credentials from AWS Secrets Manager
   - Clones/updates the ml-pipeline repository automatically
   - Configures authenticated Git remote for seamless push/pull
   - Sets up user identity and credential helper

3. **Jupyter Configuration**

   - Opens directly in `/ml-pipeline/notebooks/` directory
   - Installs project dependencies from requirements.txt
   - Configures notebook server settings

4. **Jupyter Configuration**
   - Opens directly in `/ml-pipeline/notebooks/` directory
   - Installs project dependencies from requirements.txt
   - Configures notebook server settings

### Two-Way Git Integration

**From SageMaker to GitHub:**

```bash
# In SageMaker terminal
cd /home/ec2-user/SageMaker/ml-pipeline
git add notebooks/
git commit -m "Update model from SageMaker"
git push
```

**From Local to SageMaker:**

```bash
# Locally
git push

# SageMaker automatically pulls latest changes on startup
```

## Management Commands

### Notebook Operations

```bash
make start-notebook      # Start notebook instance (ml.t3.medium)
make stop-notebook       # Stop notebook to save costs
```

### Model Management

```bash
make get-endpoints       # List SageMaker model endpoints
make get-model-artifacts # Show model artifacts in S3
make test-sagemaker      # Test deployed K-means endpoint
make update-sagemaker-proxy # Update SageMaker API proxy
```

## Model Deployment Results

- **Endpoint**: `kmeans-2025-07-31-19-58-36-067` (InService)
- **Clusters**: 5 customer segments with 0.62 silhouette score
- **Public API**: Available at `/segment` endpoint via `SageMakerProxyLambdaFunction`
- **Proxy Function**: Lambda function that proxies requests to private K-means endpoint
- **Inference**: ~150ms latency with auto-scaling (1-4 instances)

## Testing the Customer Segmentation API

### Business Purpose

The K-means customer segmentation endpoint (K=5) classifies customers into 5 distinct segments based on normalized features (Age, Income, Purchases). This enables:

- **Targeted Marketing**: Tailor campaigns to specific customer segments
- **Product Development**: Understand different customer needs and preferences
- **Resource Allocation**: Focus efforts on high-value customer segments
- **Personalization**: Customize experiences based on segment characteristics

### API Testing

```bash
# Get the current API endpoint URL
API_URL=$(make get-api-url)

# Test customer segmentation with normalized features
curl -X POST "$API_URL/segment" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      [-1.14, -1.13, 0.68],
      [-1.67, -0.81, -0.22],
      [1.10, 0.45, -0.29]
    ]
  }'
```

### Response Format

```json
{
  "predictions": [
    {
      "closest_cluster": 4.0,
      "distance_to_cluster": 0.92
    },
    {
      "closest_cluster": 4.0,
      "distance_to_cluster": 1.37
    },
    {
      "closest_cluster": 2.0,
      "distance_to_cluster": 0.98
    }
  ],
  "endpoint": "kmeans-2025-07-31-19-58-36-067",
  "model": "K-means Customer Segmentation",
  "features_processed": 3
}
```

### Understanding the Output

- **closest_cluster**: Customer segment ID (0-4, total of 5 segments)
- **distance_to_cluster**: How well the customer fits the segment (lower = better fit)
- **Business Interpretation** (5 segments from K=5):
  - Cluster 0-1: Budget-conscious customers
  - Cluster 2-3: Mid-tier customers
  - Cluster 4: Premium customers

### Alternative Testing

```bash
# Use the built-in test command
make test-sagemaker

# Get endpoint status
make get-endpoints
```

## Future Improvements

### Data Preprocessing Architecture

**Current Limitation**: The deployed SageMaker K-means endpoint expects pre-scaled data (normalized features). Users must manually transform raw values before calling the API.

**Proposed Solution**: Add a preprocessing layer using Lambda functions:

1. **Client sends raw data**:
   ```json
   {"age": 20, "income": 60000, "purchases": 10}
   ```

2. **Lambda preprocessing**:
   - Load saved `StandardScaler` from S3 (fitted during training)
   - Transform raw data to scaled format
   - Call SageMaker endpoint with scaled data

3. **Enhanced user experience**:
   - No manual scaling required
   - Business-friendly input format
   - Separation of concerns (Lambda handles preprocessing, SageMaker handles inference)

**Implementation**: Store the fitted scaler object in S3 during training, then load it in a Lambda function that sits between API Gateway and the SageMaker endpoint.

## Cost Optimization

- **Manual control**: Use `make stop-notebook` when not in use to save costs
- **Endpoint costs**: ~$0.10/hour when running
- **Notebook costs**: ~$0.05/hour when running
