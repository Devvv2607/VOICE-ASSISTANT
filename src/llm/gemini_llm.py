"""
Google Gemini LLM wrapper for LangChain integration.
"""

import google.generativeai as genai
from typing import Optional, List
from langchain.llms.base import LLM


class GeminiLLM(LLM):
    """Custom Google Gemini LLM wrapper for LangChain."""
    
    api_key: str
    model_name: str = "gemini-pro"
    max_tokens: int = 500
    temperature: float = 0.3
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize the Gemini LLM with API key."""
        super().__init__(**kwargs)
        self.api_key = api_key
        self.model_name = kwargs.get('model_name', 'gemini-pro')
        self.max_tokens = kwargs.get('max_tokens', 500)
        self.temperature = kwargs.get('temperature', 0.3)
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Gemini API."""
        try:
            # Configure generation settings
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                candidate_count=1,
            )
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "Error: No response generated from Gemini API"
            
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        return "gemini"