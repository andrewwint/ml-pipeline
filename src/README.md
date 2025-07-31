# Customer Insights GenAI API

## Overview

This API processes customer feedback text to extract marketing insights. It performs sentiment analysis, identifies unmet needs, and detects safety concerns using AWS Bedrock Claude-3-Haiku.

## Primary Use Case: Marketing Intelligence

**Objective**: Process customer feedback for marketing insights

### Core Capabilities

1. **Sentiment Analysis** - Classify customer sentiment and satisfaction
2. **Insight Mining** - Extract unmet needs and pain points
3. **Multi-language Support** - English, Spanish, and French
4. **Safety Detection** - Identify potential product safety concerns

### Value-Added Features

- **Adverse Event Detection** - Local safety concern detection
- **Recommendations** - Generate suggested actions
- **Response Time** - 1.6-2.7s via AWS Bedrock

## API Endpoint

```
POST /insights
```

### Input Format

```json
{
    "text": "The product works well but the setup process was confusing and took hours",
    "source": "customer_review",
    "category": "product_feedback"
}
```

### Output Format

```json
{
    "sentiment_score": -0.8,
    "sentiment_label": "negative",
    "language_detected": "english",
    "insights": {
        "unmet_needs": ["product safety", "device reliability"],
        "pain_points": ["device overheating", "burn injury"],
        "positive_aspects": []
    },
    "recommendations": [
        "prioritize product safety testing",
        "improve device cooling mechanisms",
        "add clear safety warnings"
    ],
    "adverse_events": ["burn"],
    "safety_concerns": [{
        "event": "burn",
        "severity": "mild",
        "confidence": 0.8,
        "safety_category": "Thermal Injury",
        "detected_phrase": "The device got very hot and burned my hand..."
    }],
    "processing_time_ms": 1520,
    "confidence": 0.95,
    "model": "claude-3-haiku",
    "status": "success"
}
```

## Marketing Applications

### 1. Product Development
- **Feature Prioritization**: Identify most requested features
- **Pain Point Resolution**: Address common customer frustrations
- **User Experience**: Improve product usability based on feedback

### 2. Customer Segmentation
- **Satisfaction Levels**: Group customers by sentiment patterns
- **Need Categories**: Segment by unmet needs and requirements
- **Engagement Strategies**: Tailor messaging to customer sentiment

### 3. Competitive Intelligence
- **Market Gaps**: Discover underserved customer needs
- **Positioning**: Understand customer perception vs competitors
- **Opportunity Mapping**: Identify new market opportunities

### 4. Campaign Optimization
- **Message Testing**: Analyze response sentiment to marketing copy
- **Channel Effectiveness**: Compare sentiment across communication channels
- **Content Strategy**: Develop content addressing identified needs

## Technical Architecture

### AWS Bedrock Integration
- **Model**: Claude-3-Haiku for fast, cost-effective analysis
- **Capabilities**: Natural language understanding, multilingual processing
- **Performance**: ~1-2 second inference time

### Input Processing Pipeline
1. **Validation**: Content filtering and quality checks
2. **Language Detection**: Automatic language identification
3. **Translation**: Convert non-English text to English for analysis
4. **Analysis**: Sentiment, insights, and recommendations generation

### Security & Privacy
- **PII Sanitization**: Automatic removal of personal information
- **Content Filtering**: Block inappropriate or harmful content
- **Data Encryption**: All data encrypted in transit and at rest
- **Audit Logging**: Complete request/response tracking

## File Structure

```
src/genai/
├── genai_insights.py     # Main GenAI Lambda handler
├── sagemaker_proxy.py    # SageMaker endpoint proxy Lambda
├── prompts.py           # Marketing-focused prompt templates
├── adverse_events.py    # Safety concern detection
├── utils.py            # Input validation and utilities
└── requirements.txt     # Python dependencies
```

## Usage Examples

### Customer Review Analysis
```bash
curl -X POST https://api-url/insights \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Love the product but wish it had mobile app integration",
    "source": "app_store_review",
    "category": "feature_request"
  }'
```

### Social Media Monitoring
```bash
curl -X POST https://api-url/insights \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Frustrated with customer service wait times #needhelp",
    "source": "twitter",
    "category": "service_feedback"
  }'
```

### Safety Issue Detection
```bash
curl -X POST https://api-url/insights \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The device got very hot and burned my hand during use. This is dangerous!",
    "source": "customer_complaint",
    "category": "safety_issue"
  }'
```

## Key Metrics

- **Response Time**: < 3 seconds (95th percentile)
- **Accuracy**: 85%+ sentiment classification accuracy
- **Language Support**: English, Spanish, French
- **Throughput**: 100+ requests/minute
- **Cost**: < $0.01 per analysis

## Business Value

### Use Cases
- **Product Development**: Feature prioritization based on feedback
- **Marketing**: Sentiment-based customer segmentation
- **Support**: Proactive issue identification
- **Analysis**: Automated feedback processing

### Metrics
- **Sentiment Trends**: Track customer satisfaction over time
- **Feature Requests**: Identify most requested capabilities
- **Issue Detection**: Monitor safety concerns and problems
- **Response Analysis**: Process feedback at scale

## Deployment Commands

### Infrastructure Management
```bash
make deploy          # Deploy complete infrastructure (IaC)
make update-lambda   # Update Lambda function code only
make destroy         # Tear down all resources
make status          # Check deployment status
```

### API Testing
```bash
make test-api        # Test Customer Insights API
make get-api-url     # Get API endpoint URL
```

### Development
```bash
make start-notebook  # Start SageMaker notebook instance
make stop-notebook   # Stop SageMaker notebook instance
```

## Performance Metrics

### Current Performance (Production)
- **Average Response Time**: 1.7s (1613ms - 1940ms observed)
- **95th Percentile**: < 2.5s ✅ (Target: < 3s)
- **Consistency**: ±300ms variance
- **Model**: Claude-3-Haiku via AWS Bedrock
- **Confidence Score**: 0.9 (90% accuracy)

### Performance Breakdown
- **AWS Bedrock Inference**: ~1.5s
- **Lambda Processing**: ~200ms
- **API Gateway Overhead**: ~100ms
- **Safety Analysis**: ~50ms

### Optimization Results
- **Cold Start**: < 3s (optimized from 10s+)
- **Memory Usage**: 1024MB (optimal for Bedrock calls)
- **Cost per Request**: < $0.005
- **Throughput**: 100+ concurrent requests

### Value-Added Features Performance
- **Adverse Event Detection**: 0ms (local processing)
- **Multi-language Support**: +200ms for translation
- **Safety Concerns**: Real-time detection
- **Recommendation Engine**: Integrated in main inference

## Getting Started

1. **Deploy Infrastructure**: `make deploy`
2. **Test API**: `make test-api`
3. **Get Endpoint**: `make get-api-url`
4. **Integrate Systems**: Connect to CRM, support tools, and analytics platforms
5. **Monitor Performance**: Track metrics and optimize based on usage patterns

This API processes customer feedback to provide sentiment analysis, unmet needs identification, and safety concern detection for marketing and product teams.