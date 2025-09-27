"""
Mistral LLM wrapper for LangChain integration.
"""

import requests
from typing import Optional, List
from langchain.llms.base import LLM


class MistralLLM(LLM):
    """Custom Mistral LLM wrapper for LangChain."""
    
    api_key: str
    model_name: str = "mistral-small-latest"
    max_tokens: int = 500
    temperature: float = 0.3
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Mistral API."""
        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('choices'):
                    return data['choices'][0]['message']['content'].strip()
            
            return "Error: Unable to get response from Mistral API"
            
        except Exception as e:
            return f"Error calling Mistral API: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        return "mistral"