import os
import time
from typing import List
from huggingface_hub import InferenceClient

# Constants
# Using Llama 3 Instruct model
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

def get_hf_token():
    token = os.getenv("HF_API_KEY")
    if not token:
        raise ValueError("HF_API_KEY environment variable is not set.")
    return token

PROMPT_TEMPLATE = """
You are a professional fashion stylist. Below are several descriptions of clothing items and outfits from a moodboard. Your task is to synthesize these descriptions into a single, cohesive "unified aesthetic" summary. 
IMPORTANT: The core target audience (and model styling) is {gender}.
Focus on the actual garments described. Do not hallucinate styles not present.
Describe the overall style, mood, color palette, and key garment types. The summary must be a concise, descriptive paragraph that can be used as a prompt for an AI image generator.

Captions:
{caption_list}

Unified Aesthetic Summary:
"""

def generate_summary(captions: List[str], gender: str) -> str:
    """
    Sends captions to Hugging Face Inference API for summarization.
    """
    client = InferenceClient(token=get_hf_token())
    
    # Format the prompt
    caption_text = "\n".join([f"- {c}" for c in captions])
    full_prompt = PROMPT_TEMPLATE.replace("{caption_list}", caption_text).replace("{gender}", gender)
    
    # Structure for Chat Completion API (standard for Llama 3 Instruct)
    messages = [
        {"role": "user", "content": full_prompt}
    ]
    
    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # We use chat_completion for Instruct models
            response = client.chat_completion(
                messages, 
                model=MODEL_ID, 
                max_tokens=150,
                temperature=0.7
            )
            # Accessing the content directly from ChatCompletionOutput
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"HF API Error (Summarization): {e}")
            if "503" in str(e) or "429" in str(e): # Overloaded
                time.sleep(5)
                continue
            
            # If 404/401/400 (Not found/Auth/Bad request), logging it but falling back
            print("WARNING: Falling back to Mock Summary due to API unavailability.")
            return "A cohesive, modern minimalist aesthetic featuring monochromatic tones, clean lines, and tailored silhouettes, suitable for high-end urban fashion photography."
            
    print("WARNING: Max retries reached. Returning Mock Summary.")
    return "A cohesive, modern minimalist aesthetic featuring monochromatic tones, clean lines, and tailored silhouettes, suitable for high-end urban fashion photography."


REFINE_TEMPLATE = """
You are a professional fashion stylist.
Current Aesthetic Description: "{current_summary}"
User Change Request: "{refinement_command}"

Task: Rewrite the aesthetic description to incorporate the user's change request. Ensure the new description is cohesive, descriptive, and ready for image generation. Do not explain the change, just provide the new description.
Updated Aesthetic Summary:
"""

def refine_summary(current_summary: str, refinement_command: str) -> str:
    """
    Rewrites the summary based on the refinement command using Llama 3.
    Falls back to smart text prepending if API unavailable.
    """
    client = InferenceClient(token=get_hf_token())
    
    full_prompt = REFINE_TEMPLATE.replace("{current_summary}", current_summary).replace("{refinement_command}", refinement_command)
    
    messages = [{"role": "user", "content": full_prompt}]
    
    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat_completion(
                messages, 
                model=MODEL_ID, 
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"HF API Error (Refinement): {e}")
            if "503" in str(e) or "429" in str(e):
                time.sleep(5)
                continue
            
            # Smart fallback: prepend the change to make it more prominent
            print("WARNING: Refinement API failed. Using smart prepend.")
            # Keep summary short and put the change at the front
            short_summary = current_summary[:200] if len(current_summary) > 200 else current_summary
            return f"{refinement_command}, {short_summary}"
            
    # Final fallback
    short_summary = current_summary[:200] if len(current_summary) > 200 else current_summary
    return f"{refinement_command}, {short_summary}"
