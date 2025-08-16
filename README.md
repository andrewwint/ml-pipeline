# ML Pipeline with Auto-Scaling

Production-ready ML pipeline for customer segmentation using AWS services, Infrastructure as Code, and GenAI integration. Features **automatic scaling**, cost optimization, and one-command deployment.

## 🚀 Quick Start

```bash
# Deploy complete infrastructure with auto-scaling
make install && make deploy

# Environment-specific deployments
make deploy-dev      # Development (1-2 instances)
make deploy-prod     # Production (2-8 instances)

# Test the APIs
make test-api        # Test GenAI insights
make test-sagemaker  # Test ML segmentation
```

## 🎯 Key Features

- **Auto-Scaling SageMaker Endpoints**: 1-4 instances, target-tracking scaling
- **Customer Segmentation**: K-means clustering (0.62 silhouette score, 150ms inference)
- **GenAI Insights**: AWS Bedrock Claude-3-Haiku (1.6-2.7s response, multi-language)
- **Infrastructure as Code**: Complete CloudFormation automation
- **Cost Optimized**: Auto-scaling + manual notebook controls

## 📋 Assessment Tasks

| Task                           | Implementation                                            | Performance                            |
| ------------------------------ | --------------------------------------------------------- | -------------------------------------- |
| **1. Customer Segmentation**   | K-means clustering, **auto-scaling 1-4 instances**        | 150ms inference, 0.62 silhouette score |
| **2. Infrastructure as Code**  | CloudFormation with auto-scaling, security, cost controls | One-command deployment                 |
| **3. GenAI Customer Insights** | AWS Bedrock Claude-3-Haiku, multi-language support        | 1.6-2.7s response, 90% confidence      |

📖 **Detailed Documentation**: [notebooks/](notebooks/) • [src/README.md](src/README.md) • [docs/architecture.md](docs/architecture.md)

## 🔗 API Endpoints

```bash
# Get your API URLs
make get-api-url        # GenAI insights endpoint
make get-sagemaker-api-url  # ML segmentation endpoint

# Test the APIs
make test-api           # Test GenAI with sample data
make test-sagemaker     # Test ML clustering with sample data
```

**Example Usage**: See [src/README.md](src/README.md) for detailed API documentation and examples.

## ⚡ Setup & Deployment

### Prerequisites

- AWS Account with CLI configured (`aws configure`)
- Python 3.9+
- GitHub Personal Access Token (for SageMaker integration)

### One-Command Deployment

```bash
git clone <repository-url> && cd ml-pipeline
make install && make deploy
```

### Environment-Specific Deployments

```bash
make deploy-dev      # Development: 1-2 instances, cost-optimized
make deploy-prod     # Production: 2-8 instances, high availability
make deploy-custom   # Interactive: custom scaling parameters
```

### Monitoring & Management

```bash
make get-scaling     # Check auto-scaling status
make get-endpoints   # List endpoints with instance counts
make start-notebook  # Start SageMaker notebook
make stop-notebook   # Stop notebook (cost savings)
make destroy         # Clean up all resources
```

## 🏗️ Architecture Highlights

- **Auto-Scaling**: SageMaker endpoints (1-4 instances) with target-tracking
- **Cost Optimization**: Auto scale-down + manual notebook controls
- **Security**: IAM least privilege, S3 encryption, API Gateway CORS
- **Monitoring**: CloudWatch logs, scaling metrics, performance tracking

**Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) • Quick fix: `make force-destroy` for cleanup

## 📊 Performance Metrics

| Metric                | Target  | Achieved                     | Status              |
| --------------------- | ------- | ---------------------------- | ------------------- |
| **SageMaker Latency** | < 200ms | ~150ms                       | ✅ 25% better       |
| **GenAI Response**    | < 3s    | 1.6-2.7s                     | ✅ Sub-3s met       |
| **Model Accuracy**    | > 0.5   | 0.62                         | ✅ 24% above        |
| **Auto-Scaling**      | -       | 1-4 instances, 60s scale-out | ✅ Production-ready |

## 📁 Project Structure

```
ml-pipeline/
├── infrastructure/cloudformation-complete.yaml  # Complete IaC with auto-scaling
├── src/genai/                                   # GenAI Lambda functions
├── notebooks/CustomerSegmentation.ipynb         # ML model development
├── data/customer_segmentation_data.csv          # Dataset (1000 customers)
├── docs/                                        # Architecture documentation
└── Makefile                                     # Deployment automation
```

## 🔗 Additional Resources

- **Architecture**: [docs/architecture.md](docs/architecture.md)
- **API Documentation**: [src/README.md](src/README.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Notebooks**: [notebooks/README.md](notebooks/README.md)
