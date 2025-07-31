# ML Pipeline Architecture

## System Overview

The ML Pipeline is designed as a cloud-native, serverless architecture leveraging AWS services for scalability, reliability, and cost-effectiveness. The system follows a microservices approach with clear separation of concerns between data processing, model training, inference, and monitoring components.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            API Layer                                     │
│  ┌─────────────────┐                           ┌──────────────────┐   │
│  │  REST API       │                           │  GenAI Lambda    │   │
│  │  (API Gateway)  │───────────────────────────│  (Claude-3-Haiku)│   │
│  └─────────────────┘                           └──────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                          ML Platform Layer                               │
│  ┌─────────────────┐                           ┌──────────────────┐   │
│  │  SageMaker      │                           │  SageMaker       │   │
│  │  Notebook       │───────────────────────────│  K-means Endpoint│   │
│  └─────────────────┘                           └──────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                          Data Storage Layer                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐   │
│  │  S3 Data        │    │  S3 Models      │    │  S3 Logs         │   │
│  │  Bucket         │    │  Bucket         │    │  Bucket          │   │
│  └─────────────────┘    └─────────────────┘    └──────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                      Security & IAM Layer                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐   │
│  │  CloudWatch     │    │  IAM Roles      │    │  S3              │   │
│  │  Logs           │    │  & Policies     │    │  Encryption      │   │
│  └─────────────────┘    └─────────────────┘    └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer

#### API Gateway

- **Purpose**: RESTful API endpoint for GenAI insights
- **Implemented Features**:
  - Basic REST API with POST method
  - CORS configuration
  - Lambda proxy integration

#### Lambda Functions

- **GenAI Insights Lambda**:
  - AWS Bedrock Claude-3-Haiku integration
  - Customer feedback sentiment analysis
  - Unmet needs and safety concern detection
  - Multi-language support (English, Spanish, French)
  - Response time: 1.6-2.7s

### 2. ML Platform Layer

#### SageMaker Components

**Notebook Instance**:

- **Instance Type**: ml.t3.medium
- **Purpose**: Interactive development and experimentation
- **Features**:
  - Pre-installed ML libraries
  - Direct S3 access
  - Git integration

**K-means Endpoint**:

- **Instance Type**: ml.m5.large
- **Configuration**:
  - Single model endpoint for customer segmentation
  - Real-time inference (~150ms latency)
  - Deployed via notebook (not automated training jobs)

### 3. Data Storage Layer

#### S3 Buckets

**Data Bucket**:

```
s3://ml-pipeline-data-{account-id}/
├── raw/                  # Original data files
├── processed/            # Preprocessed data
├── features/             # Feature engineering outputs
└── validation/           # Test/validation datasets
```

**Models Bucket**:

```
s3://ml-pipeline-models-{account-id}/
├── training/             # Training artifacts
├── production/           # Production models
├── archive/              # Historical models
└── metadata/             # Model metadata
```

**Logs Bucket**:

```
s3://ml-pipeline-logs-{account-id}/
├── training/             # Training logs
├── inference/            # Prediction logs
├── api/                  # API access logs
└── system/               # System logs
```

### 4. Security Architecture

#### IAM Roles

**SageMaker Execution Role**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::ml-pipeline-*/*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

**Lambda Execution Role**:

- SageMaker endpoint invocation
- S3 read access
- CloudWatch logs write
- X-Ray tracing

#### Encryption

- **At Rest**: S3 AES256 encryption (basic)
- **In Transit**: TLS via API Gateway and AWS services
- **Key Management**: AWS managed keys (not custom KMS)

### 5. Monitoring & Observability

#### CloudWatch Logs

- **Lambda Logs**: Automatic logging for GenAI function
- **Basic Monitoring**: Response times tracked in application code
- **Stack Outputs**: Resource information via CloudFormation

**Note**: Advanced monitoring (custom dashboards, alarms, X-Ray tracing) not implemented in current version.

## Data Flow

### Training Pipeline

1. Raw data uploaded to S3 data bucket
2. SageMaker notebook triggers preprocessing
3. Training job reads processed data
4. Model artifacts stored in S3 models bucket
5. Model registered in SageMaker Model Registry
6. Endpoint configuration created
7. Model deployed to endpoint

### Inference Pipeline

1. Client sends request to API Gateway
2. Lambda function validates request
3. Lambda invokes SageMaker endpoint
4. Model returns predictions
5. Lambda transforms response
6. Response returned to client
7. Metrics logged to CloudWatch

### GenAI Pipeline

1. Client sends customer feedback text to API
2. Lambda validates and processes input
3. Local adverse event detection performed
4. AWS Bedrock Claude generates marketing insights
5. Safety concerns and recommendations returned
6. Response logged to CloudWatch

## Scalability Considerations

### Horizontal Scaling

- **API Gateway**: Automatically scales
- **Lambda**: Concurrent execution limits (1000 default)
- **SageMaker Endpoints**: Auto-scaling 1-4 instances
- **S3**: Virtually unlimited storage

### Vertical Scaling

- **Training**: Up to ml.p3.16xlarge for GPU
- **Inference**: Instance type upgrades
- **Lambda**: Memory allocation up to 10GB

### Performance Optimization

- **Caching**: CloudFront for static content
- **Model Optimization**: SageMaker Neo compilation
- **Batch Transform**: For high-volume predictions
- **Multi-model Endpoints**: Reduced infrastructure costs

## Disaster Recovery

### Backup Strategy

- **Data**: S3 cross-region replication
- **Models**: Versioned artifacts in S3
- **Configuration**: Infrastructure as Code in Git

### Recovery Procedures

- **RPO**: 1 hour for data, immediate for models
- **RTO**: 30 minutes for full system recovery
- **Failover**: Multi-AZ deployments

## Cost Optimization (Implemented)

### Compute Optimization

- **SageMaker Notebook**: Auto-shutdown after 30 minutes inactivity
- **Resource Tagging**: Basic cost tracking tags

### Storage Optimization

- **S3 Lifecycle**: 30-day retention for logs bucket
- **Versioning**: Enabled for data and model buckets

**Note**: Advanced cost optimization (spot instances, intelligent tiering, budget alerts) not implemented.

## Security (Implemented)

### Access Control

- **IAM Roles**: Least privilege for SageMaker and Lambda
- **S3 Bucket Policies**: Minimal required permissions
- **API Gateway**: Basic CORS configuration

### Data Protection

- **S3 Encryption**: AES256 at rest
- **Public Access**: Blocked on all S3 buckets

**Note**: Advanced security (VPC endpoints, WAF, MFA enforcement) not implemented in current version.ance

- CloudTrail for audit logging
- AWS Config for compliance rules
- Regular security assessments
- Data retention policies

## Future Architecture Enhancements

### Phase 1: Enhanced Monitoring

- Prometheus/Grafana integration
- Custom CloudWatch dashboards
- Automated anomaly detection
- Real-time alerting

### Phase 2: Multi-Region

- Active-active deployment
- Global accelerator
- Cross-region replication
- Latency-based routing

### Phase 3: Advanced ML Features

- Online learning pipeline
- Feature store integration
- Model versioning API
- A/B testing framework

### Phase 4: Edge Deployment

- SageMaker Edge Manager
- IoT integration
- Local inference
- Federated learning
