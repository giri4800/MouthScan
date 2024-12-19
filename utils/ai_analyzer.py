
import logging
import os
import base64
import anthropic
from typing import Tuple

class AIAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def analyze_image(self, image_path: str) -> Tuple[str, float]:
        """
        Analyze the image using Anthropic's API and return result and confidence
        """
        try:
            self.logger.info(f"Analyzing image: {image_path}")
            
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Send to Anthropic API
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a dental analysis assistant. Analyze this dental image and provide your analysis in this exact format (no other text): Normal,0.95 or Abnormal,0.85 where the first part is your assessment and the second is your confidence score."
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }]
            )

            # Parse response - expecting format like "Normal,0.95" or "Abnormal,0.85"
            response_text = message.content[0].text.strip()
            result, confidence = response_text.split(',')
            
            return result, float(confidence)
            
        except Exception as e:
            self.logger.error(f"Error analyzing image: {str(e)}")
            raise Exception("Failed to analyze image") from e
