"""
Prompt templates for patient treatment analysis.
"""

SENTIMENT_ANALYSIS_PROMPT = """
Analyze the sentiment of this EPKINLY patient treatment journal entry.
Consider medical context and treatment-related emotions.

Patient Entry: {patient_entry}

Respond with JSON:
{{
    "sentiment_score": float(-1 to 1),
    "sentiment_label": "positive|negative|neutral|mixed",
    "confidence": float(0 to 1)
}}
"""

ADVERSE_EVENT_PROMPT = """
Identify potential adverse events in this EPKINLY patient entry.
Focus on symptoms, side effects, and treatment-related issues.

Patient Entry: {patient_entry}

Known EPKINLY side effects: fatigue, nausea, headache, fever, chills, 
injection site reactions, decreased appetite, diarrhea, muscle pain, 
joint pain, rash, dizziness.

Respond with JSON array of adverse events found:
{{
    "adverse_events": [
        {{
            "event": "symptom name",
            "severity": "mild|moderate|severe", 
            "confidence": float(0 to 1),
            "medical_term": "clinical terminology"
        }}
    ]
}}
"""

LANGUAGE_DETECTION_PROMPT = """
Detect the language of this patient entry and translate to English if needed.

Patient Entry: {patient_entry}

Respond with JSON:
{{
    "language_detected": "english|spanish|french|other",
    "english_translation": "translated text or original if English",
    "confidence": float(0 to 1)
}}
"""

COMPREHENSIVE_ANALYSIS_PROMPT = """
You are a medical AI assistant analyzing patient journal entries for EPKINLY therapy.
Provide comprehensive analysis including sentiment, language, adverse events, and recommendations.

Patient Entry: "{patient_entry}"

Analysis Guidelines:
1. Sentiment: Consider treatment context, hope vs. concern
2. Language: Detect and translate if needed
3. Adverse Events: Look for known EPKINLY side effects
4. Recommendations: Provide actionable medical guidance

Known EPKINLY side effects:
- Fatigue, nausea, headache, fever, chills
- Injection site reactions, decreased appetite, diarrhea
- Muscle pain, joint pain, rash, dizziness

Respond ONLY with valid JSON:
{{
    "sentiment_score": float(-1 to 1),
    "sentiment_label": "positive|negative|neutral|mixed",
    "language_detected": "english|spanish|french|other",
    "english_translation": "translated text or original if English",
    "adverse_events": [
        {{
            "event": "symptom name",
            "severity": "mild|moderate|severe",
            "confidence": float(0 to 1),
            "medical_term": "clinical terminology"
        }}
    ],
    "recommendations": [
        "actionable recommendation 1",
        "actionable recommendation 2"
    ]
}}
"""

def get_prompt_template(prompt_type: str) -> str:
    """
    Get a specific prompt template by type.
    
    Args:
        prompt_type: Type of prompt (sentiment, adverse_event, language, comprehensive)
        
    Returns:
        Prompt template string
    """
    templates = {
        'sentiment': SENTIMENT_ANALYSIS_PROMPT,
        'adverse_event': ADVERSE_EVENT_PROMPT,
        'language': LANGUAGE_DETECTION_PROMPT,
        'comprehensive': COMPREHENSIVE_ANALYSIS_PROMPT
    }
    
    return templates.get(prompt_type, COMPREHENSIVE_ANALYSIS_PROMPT)