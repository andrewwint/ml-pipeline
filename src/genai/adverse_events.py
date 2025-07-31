"""
Adverse Event detection logic for customer feedback safety concerns.
"""

from typing import List, Dict, Any
import re


# Product safety concerns with keywords and severity indicators
SAFETY_CONCERNS = {
    'injury': {
        'keywords': ['injury', 'hurt', 'injured', 'wound', 'cut', 'bruise', 'broken'],
        'severity_indicators': {
            'minor': ['small', 'slight', 'little'],
            'moderate': ['bad', 'serious'],
            'severe': ['major', 'severe', 'emergency']
        }
    },
    'allergic_reaction': {
        'keywords': ['allergic', 'allergy', 'reaction', 'rash', 'swelling', 'itchy'],
        'severity_indicators': {
            'minor': ['mild', 'slight'],
            'moderate': ['bad', 'uncomfortable'],
            'severe': ['severe', 'anaphylaxis', 'emergency']
        }
    },
    'burn': {
        'keywords': ['burn', 'burned', 'burning', 'hot', 'scalded'],
        'severity_indicators': {
            'minor': ['small', 'minor'],
            'moderate': ['painful', 'blistered'],
            'severe': ['severe', 'third degree']
        }
    },
    'toxic_exposure': {
        'keywords': ['toxic', 'poison', 'chemical', 'fumes', 'exposure'],
        'severity_indicators': {
            'minor': ['mild', 'slight'],
            'moderate': ['sick', 'nauseous'],
            'severe': ['poisoned', 'emergency']
        }
    },
    'electrical_hazard': {
        'keywords': ['shock', 'electric', 'electrical', 'sparks', 'short circuit'],
        'severity_indicators': {
            'minor': ['small', 'minor'],
            'moderate': ['painful', 'burned'],
            'severe': ['severe', 'unconscious']
        }
    },
    'choking_hazard': {
        'keywords': ['choke', 'choking', 'swallowed', 'stuck', 'throat'],
        'severity_indicators': {
            'minor': ['small', 'coughed up'],
            'moderate': ['difficulty', 'breathing'],
            'severe': ['can\'t breathe', 'emergency']
        }
    }
}


def detect_adverse_events(text: str) -> List[Dict[str, Any]]:
    """
    Detect potential safety concerns in customer feedback using keyword matching.
    
    Args:
        text: Customer feedback text
        
    Returns:
        List of detected safety concerns with severity and confidence
    """
    detected_events = []
    text_lower = text.lower()
    
    for event_name, event_data in SAFETY_CONCERNS.items():
        # Check if any keywords are present
        for keyword in event_data['keywords']:
            if keyword in text_lower:
                severity = determine_severity(text_lower, event_data['severity_indicators'])
                confidence = calculate_confidence(text_lower, keyword, event_data)
                
                detected_events.append({
                    'event': event_name.replace('_', ' '),
                    'severity': severity,
                    'confidence': confidence,
                    'safety_category': get_safety_category(event_name),
                    'detected_phrase': extract_context(text, keyword)
                })
                break  # Only detect each event once
    
    return detected_events


def determine_severity(text: str, severity_indicators: Dict[str, List[str]]) -> str:
    """
    Determine severity based on context words.
    
    Args:
        text: Patient text (lowercase)
        severity_indicators: Dictionary of severity levels and their indicators
        
    Returns:
        Severity level: mild, moderate, or severe
    """
    for severity, indicators in severity_indicators.items():
        for indicator in indicators:
            if indicator in text:
                return severity
    
    return 'mild'  # Default to mild if no severity indicators found


def calculate_confidence(text: str, keyword: str, event_data: Dict) -> float:
    """
    Calculate confidence score for adverse event detection.
    
    Args:
        text: Patient text (lowercase)
        keyword: Detected keyword
        event_data: Event configuration data
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    base_confidence = 0.7
    
    # Increase confidence if multiple keywords for same event are present
    keyword_count = sum(1 for kw in event_data['keywords'] if kw in text)
    if keyword_count > 1:
        base_confidence += 0.1
    
    # Increase confidence if severity indicators are present
    severity_found = any(
        indicator in text 
        for indicators in event_data['severity_indicators'].values()
        for indicator in indicators
    )
    if severity_found:
        base_confidence += 0.1
    
    # Decrease confidence for negations
    negations = ['no', 'not', 'without', 'never', 'none']
    keyword_pos = text.find(keyword)
    if keyword_pos > 0:
        preceding_text = text[max(0, keyword_pos-20):keyword_pos]
        if any(neg in preceding_text for neg in negations):
            base_confidence -= 0.3
    
    return min(1.0, max(0.1, base_confidence))


def get_safety_category(event_name: str) -> str:
    """
    Get the safety category for a detected concern.
    
    Args:
        event_name: Internal event name
        
    Returns:
        Safety category
    """
    safety_categories = {
        'injury': 'Physical Harm',
        'allergic_reaction': 'Allergic Response',
        'burn': 'Thermal Injury',
        'toxic_exposure': 'Chemical Hazard',
        'electrical_hazard': 'Electrical Safety',
        'choking_hazard': 'Airway Obstruction'
    }
    
    return safety_categories.get(event_name, event_name.replace('_', ' ').title())


def extract_context(text: str, keyword: str, context_length: int = 30) -> str:
    """
    Extract context around a detected keyword.
    
    Args:
        text: Original customer feedback text
        keyword: Detected keyword
        context_length: Number of characters to include on each side
        
    Returns:
        Context string around the keyword
    """
    text_lower = text.lower()
    keyword_pos = text_lower.find(keyword.lower())
    
    if keyword_pos == -1:
        return keyword
    
    start = max(0, keyword_pos - context_length)
    end = min(len(text), keyword_pos + len(keyword) + context_length)
    
    context = text[start:end].strip()
    
    # Add ellipsis if we truncated
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
    
    return context


def validate_adverse_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate and filter safety concerns based on confidence and relevance.
    
    Args:
        events: List of detected safety concerns
        
    Returns:
        Filtered list of validated safety concerns
    """
    validated_events = []
    
    for event in events:
        # Only include events with confidence > 0.3
        if event.get('confidence', 0) > 0.3:
            validated_events.append(event)
    
    # Remove duplicates (same event name)
    seen_events = set()
    unique_events = []
    
    for event in validated_events:
        event_name = event.get('event')
        if event_name not in seen_events:
            seen_events.add(event_name)
            unique_events.append(event)
    
    return unique_events