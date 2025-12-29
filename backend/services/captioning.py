import io
from typing import List
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load model once at startup (will download ~500MB on first run)
print("Loading BLIP model (this may take a moment on first run)...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
print("BLIP model loaded successfully!")

def generate_caption(image_bytes: bytes) -> str:
    """
    Generates a caption for an image using local BLIP model.
    No API dependency - runs entirely on your machine.
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Process image
        inputs = processor(image, return_tensors="pt")
        
        # Generate caption
        output = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(output[0], skip_special_tokens=True)
        
        if caption and len(caption) > 5:
            return caption
        else:
            return "Could not analyze image. Please describe manually."
            
    except Exception as e:
        print(f"BLIP Error: {e}")
        return f"⚠️ Analysis failed. Please describe this item manually."

def generate_captions_for_images(images: List[bytes]) -> List[str]:
    """
    Process a list of image bytes and return text captions using local BLIP.
    """
    captions = []
    for img_bytes in images:
        try:
            caption = generate_caption(img_bytes)
            captions.append(caption)
        except Exception as e:
            captions.append(f"Error: {str(e)}")
    return captions
