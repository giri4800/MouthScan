import os
import base64
import logging
import anthropic
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY')
        )

    def _encode_image(self, image_path):
        try:
            with Image.open(image_path) as img:
                # Ensure the image is in RGB mode
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if the image is too large (max 4096x4096)
                max_size = 4096
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size))
                
                # Convert to base64
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return f"data:image/jpeg;base64,{img_str}"
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            raise

    def analyze_image(self, image_path):
        """
        Analyze an image for signs of oral cancer using Claude Vision.
        Returns a tuple of (result, confidence)
        """
        try:
            encoded_image = self._encode_image(image_path)
            
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.0,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this oral cavity image for potential signs of mouth cancer. Focus on identifying any suspicious lesions, discolorations, or abnormal growths. Provide your analysis as a JSON-like response with two fields: 'result' (either 'Normal' or 'Suspicious') and 'confidence' (a float between 0 and 1). If suspicious, also note the specific concerning features."
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": encoded_image
                            }
                        }
                    ]
                }]
            )

            # Extract the response and parse it
            response = message.content[0].text
            if "Normal" in response:
                return "Normal", 0.95
            else:
                return "Suspicious - Requires Medical Attention", 0.85

        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return "Error - Analysis Failed", 0.0
