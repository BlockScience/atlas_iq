import spacy
from typing import Dict, Any

class ResponseProcessor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def validate_response(self, response: str) -> bool:
        doc = self.nlp(response)
        # Check for specific entities or linguistic features
        if len(doc) > 0:
            return True
        return False

    def extract_information(self, response: str) -> Dict[str, Any]:
        doc = self.nlp(response)
        # Extract relevant information from the response
        # Implement custom logic as needed
        return {"text": response}
