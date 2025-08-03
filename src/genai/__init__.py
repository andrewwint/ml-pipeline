"""GenAI module for customer insights processing."""

from .genai_insights import handler as genai_handler
from .sagemaker_proxy import handler as sagemaker_handler
from .utils import validate_input
from .adverse_events import detect_adverse_events
