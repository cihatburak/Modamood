import io
import torch
from diffusers import AutoPipelineForText2Image

# Detect device - use MPS (Metal) on Mac, CUDA on NVIDIA, else CPU
if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

print(f"Loading SD Turbo model on {DEVICE} (this may take a moment on first run)...")

# Load SD Turbo - much faster than SDXL
# Model will be downloaded (~5GB) on first run
pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sd-turbo",
    torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32,
    variant="fp16" if DEVICE != "cpu" else None
)
pipe = pipe.to(DEVICE)
print(f"SD Turbo model loaded successfully on {DEVICE}!")

def generate_outfit_image(aesthetic_summary: str, gender: str = "Neutral/Unisex") -> bytes:
    """
    Generates an image based on the aesthetic summary using local SD Turbo.
    Returns image bytes.
    """
    # Determine model gender for prompt
    if gender == "Menswear":
        model_desc = "handsome male model, man, masculine"
    elif gender == "Womenswear":
        model_desc = "beautiful female model, woman, feminine"
    else:
        model_desc = "fashion model"
    
    # Prompt Engineering with explicit gender
    full_prompt = f"high quality fashion photography, {model_desc} wearing a full outfit, {aesthetic_summary}, professional lighting, detailed, sharp focus, full body shot"
    
    print(f"Generating image with prompt: {full_prompt[:80]}...")
    
    try:
        # SD Turbo only needs 1-4 steps!
        image = pipe(
            prompt=full_prompt,
            num_inference_steps=4,  # Turbo is optimized for 1-4 steps
            guidance_scale=0.0,     # Turbo doesn't need CFG
        ).images[0]
        
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        print("Image generated successfully!")
        return img_byte_arr.getvalue()
        
    except Exception as e:
        print(f"Generation Error: {e}")
        # Fallback to placeholder
        from PIL import Image
        img = Image.new('RGB', (512, 512), color=(200, 200, 200))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
