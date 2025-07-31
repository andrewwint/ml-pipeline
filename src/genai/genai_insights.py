"""
Customer Insights GenAI Lambda Function

This Lambda function processes free-form customer text to extract marketing insights,
perform sentiment analysis, and identify unmet customer needs using AWS Bedrock Claude.
Includes adverse event detection and multi-language support as value-added featuress.
"""

import json
import boto3
import os
import time
from typing import Dict, List, Any, Optional
from .adverse_events import detect_adverse_events, validate_adverse_events


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for customer insights GenAI analysis.
    
    Args:
        event: API Gateway event containing customer feedback text
        context: Lambda context object
        
    Returns:
        API Gateway response with marketing insights
    """
    start_time = time.time()
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract customer feedback fields
        text = body.get('text', '')
        source = body.get('source', 'unknown')
        category = body.get('category', 'general')
        
        # Validate input
        if not text.strip():
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Text field is required',
                    'status': 'error'
                })
            }
        
        # Process customer text for insights
        customer_text = text.strip()
        
        # Detect safety concerns using local analysis
        safety_events = detect_adverse_events(customer_text)
        validated_events = validate_adverse_events(safety_events)
        
        # Process with Bedrock Claude for marketing insights
        insights = process_with_bedrock(customer_text, source, category)
        
        # Merge local safety detection with Bedrock insights
        if validated_events:
            insights['adverse_events'] = [event['event'] for event in validated_events]
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build marketing insights response
        response_data = {
            'sentiment_score': insights.get('sentiment_score', 0.0),
            'sentiment_label': insights.get('sentiment_label', 'neutral'),
            'language_detected': insights.get('language_detected', 'english'),
            'insights': {
                'unmet_needs': insights.get('unmet_needs', []),
                'pain_points': insights.get('pain_points', []),
                'positive_aspects': insights.get('positive_aspects', [])
            },
            'recommendations': insights.get('recommendations', []),
            'adverse_events': insights.get('adverse_events', []),  # Value-add feature
            'safety_concerns': validated_events,  # Detailed safety analysis
            'processing_time_ms': processing_time,
            'confidence': insights.get('confidence', 0.0),
            'model': 'claude-3-haiku',
            'status': 'success'
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'status': 'error'
            })
        }


def process_with_bedrock(customer_text: str, source: str, category: str) -> Dict[str, Any]:
    """
    Process customer text using AWS Bedrock Claude for marketing insights.
    
    Args:
        customer_text: Customer feedback text
        source: Source of the feedback (review, survey, social, etc.)
        category: Category of feedback (product, service, pricing, etc.)
        
    Returns:
        Dictionary containing marketing insights
    """
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))
        
        # Create marketing analysis prompt
        prompt = create_marketing_prompt(customer_text, source, category)
        
        # Call Bedrock Claude
        response = bedrock.invoke_model(
            modelId=os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0'),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        claude_response = response_body['content'][0]['text']
        
        # Parse Claude's JSON response
        return json.loads(claude_response)
        
    except Exception as e:
        print(f"Bedrock processing error: {str(e)}")
        # Return fallback response
        return {
            'sentiment_score': 0.0,
            'sentiment_label': 'neutral',
            'language_detected': 'english',
            'unmet_needs': [],
            'pain_points': [],
            'positive_aspects': [],
            'adverse_events': [],
            'recommendations': ['Unable to process with GenAI - using fallback'],
            'confidence': 0.0
        }


def create_marketing_prompt(customer_text: str, source: str, category: str) -> str:
    """
    Create a marketing analysis prompt for Claude.
    
    Args:
        customer_text: Customer feedback text
        source: Source of the feedback
        category: Category of feedback
        
    Returns:
        Formatted prompt for marketing analysis
    """
    return f"""
You are a marketing AI assistant analyzing customer feedback to extract business insights.
Analyze the following customer text for marketing intelligence and unmet needs.

Customer Text: "{customer_text}"
Source: {source}
Category: {category}

Analyze for:
1. Sentiment analysis (-1 to 1 scale)
2. Language detection
3. Unmet customer needs
4. Pain points and frustrations
5. Positive aspects mentioned
6. Marketing recommendations
7. Potential adverse events or safety concerns

Respond ONLY with valid JSON in this exact format:
{{
    "sentiment_score": 0.0,
    "sentiment_label": "positive|negative|neutral|mixed",
    "language_detected": "english|spanish|french|other",
    "unmet_needs": ["need1", "need2"],
    "pain_points": ["pain1", "pain2"],
    "positive_aspects": ["positive1", "positive2"],
    "recommendations": ["rec1", "rec2"],
    "adverse_events": ["event1", "event2"],
    "confidence": 0.85
}}
"""


