"""
Utility functions for GenAI Lambda processing.
"""

import json
import re
from typing import Dict, Any, Optional
import boto3


def sanitize_patient_input(text: str) -> str:
    """
    Sanitize patient input to remove potential PII and harmful content.
    
    Args:
        text: Raw patient input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potential phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove potential email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove potential SSN patterns
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Limit length to prevent abuse
    if len(text) > 1000:
        text = text[:1000] + "..."
    
    return text.strip()


def validate_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Validate and parse JSON response from Claude.
    
    Args:
        response_text: Raw response text from Claude
        
    Returns:
        Parsed JSON dict or None if invalid
    """
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            # Try parsing the entire response
            return json.loads(response_text)
    except (json.JSONDecodeError, AttributeError):
        return None


def create_fallback_response(patient_text: str) -> Dict[str, Any]:
    """
    Create a fallback response when GenAI processing fails.
    
    Args:
        patient_text: Original patient text
        
    Returns:
        Fallback response dictionary
    """
    return {
        'sentiment_score': 0.0,
        'sentiment_label': 'neutral',
        'language_detected': 'english',
        'english_translation': patient_text,
        'adverse_events': [],
        'recommendations': [
            'Please consult with your healthcare provider',
            'Continue monitoring your symptoms'
        ]
    }


def log_custom_metric(metric_name: str, value: float, unit: str = 'Count') -> None:
    """
    Log custom CloudWatch metric for monitoring.
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Metric unit (Count, Seconds, etc.)
    """
    try:
        cloudwatch = boto3.client('cloudwatch')
        cloudwatch.put_metric_data(
            Namespace='PatientTracker/GenAI',
            MetricData=[{
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }]
        )
    except Exception as e:
        print(f"Failed to log metric {metric_name}: {str(e)}")


def detect_language_simple(text: str) -> str:
    """
    Simple language detection based on common words.
    
    Args:
        text: Input text
        
    Returns:
        Detected language: english, spanish, french, or other
    """
    text_lower = text.lower()
    
    # Spanish indicators
    spanish_words = ['me', 'siento', 'estoy', 'tengo', 'dolor', 'cansado', 'bien', 'mal']
    spanish_count = sum(1 for word in spanish_words if word in text_lower)
    
    # French indicators  
    french_words = ['je', 'suis', 'me', 'sens', 'douleur', 'fatigue', 'bien', 'mal']
    french_count = sum(1 for word in french_words if word in text_lower)
    
    # English indicators
    english_words = ['i', 'am', 'feel', 'have', 'pain', 'tired', 'good', 'bad']
    english_count = sum(1 for word in english_words if word in text_lower)
    
    # Determine language based on highest count
    counts = {
        'spanish': spanish_count,
        'french': french_count, 
        'english': english_count
    }
    
    detected_lang = max(counts, key=counts.get)
    
    # If no clear winner, default to English
    if counts[detected_lang] == 0:
        return 'english'
    
    return detected_lang


def format_processing_time(start_time: float, end_time: float) -> int:
    """
    Format processing time in milliseconds.
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp
        
    Returns:
        Processing time in milliseconds
    """
    return int((end_time - start_time) * 1000)


def create_api_response(status_code: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create standardized API Gateway response.
    
    Args:
        status_code: HTTP status code
        data: Response data
        
    Returns:
        API Gateway response format
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(data)
    }


def extract_patient_fields(body: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract and validate patient entry fields.
    
    Args:
        body: Request body dictionary
        
    Returns:
        Dictionary with extracted patient fields
    """
    return {
        'dose': sanitize_patient_input(body.get('dose', '')),
        'feeling': sanitize_patient_input(body.get('feeling', '')),
        'notes': sanitize_patient_input(body.get('notes', '')),
        'date': body.get('date', ''),
        'next_appointment': body.get('next_appointment', '')
    }