import os
import base64
import logging
from pathlib import Path
import anthropic
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        try:
            self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
            raise

    def _encode_image(self, image_path):
        """Encode image to base64 format for API submission."""
        try:
            # Convert string path to Path object
            path = Path(image_path)
            if not path.exists():
                logger.error(f"Image file not found: {image_path}")
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            with Image.open(path) as img:
                # Ensure the image is in RGB mode
                if img.mode != 'RGB':
                    logger.debug(f"Converting image from {img.mode} to RGB")
                    img = img.convert('RGB')
                
                # Resize if the image is too large
                max_size = 4096
                if img.width > max_size or img.height > max_size:
                    logger.debug(f"Resizing image from {img.width}x{img.height} to max {max_size}x{max_size}")
                    img.thumbnail((max_size, max_size))
                
                # Convert to base64
                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=95)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                logger.debug("Image successfully encoded to base64")
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
            logger.info(f"Starting analysis of image: {image_path}")
            encoded_image = self._encode_image(image_path)
            
            # Use Claude 3 Haiku for faster response times and lower costs
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.0,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this oral cavity image for potential signs of mouth cancer. Focus on:\n"
                                   "1. Suspicious lesions or ulcers\n"
                                   "2. Unusual patches (white, red, or mixed)\n"
                                   "3. Unexplained swelling or lumps\n"
                                   "4. Texture changes in the oral tissue\n"
                                   "Provide a concise assessment with your confidence level (0-100%)."
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": encoded_image.split(',')[1]  # Remove the data:image/jpeg;base64, prefix
                            }
                        }
                    ]
                }]
            )
            
            # Extract and process the response
            if message.content:
                response_text = message.content[0].text
                logger.info(f"Received analysis response: {response_text}")
                
                # Extract confidence level (default to 70% if not found)
                confidence = 0.7
                if "%" in response_text:
                    try:
                        confidence_str = response_text.split("%")[0][-3:].strip()
                        confidence = float(confidence_str) / 100
                    except (ValueError, IndexError):
                        logger.warning("Could not parse confidence level from response")
                
                return response_text.split('\n')[0], confidence  # Return first line and confidence

        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return "Error - Analysis Failed", 0.0
