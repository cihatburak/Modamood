from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from typing import List, Dict, Optional
from pydantic import BaseModel
from backend.services import captioning, summarization, generation

router = APIRouter()

@router.post("/caption_images")
async def caption_images(files: List[UploadFile] = File(...)):
    """
    Endpoint to receive list of images and return captions.
    """
    image_bytes_list = []
    try:
        for file in files:
            content = await file.read()
            image_bytes_list.append(content)
            
        captions = captioning.generate_captions_for_images(image_bytes_list)
        return {"captions": captions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SummaryRequest(BaseModel):
    captions: List[str]
    gender: str = "Neutral/Unisex"

@router.post("/summarize_aesthetic")
async def summarize_aesthetic(request: SummaryRequest):
    """
    Endpoint to receive list of captions and return aesthetic summary.
    """
    try:
        summary = summarization.generate_summary(request.captions, request.gender)
        return {"summary": summary}
        
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

class GenerateRequest(BaseModel):
    aesthetic_summary: str
    gender: str = "Neutral/Unisex"
    refinement_command: Optional[str] = None

@router.post("/generate_outfit")
async def generate_outfit(request: GenerateRequest):
    """
    Endpoint to generate outfit image from summary.
    Returns JSON with base64 image and updated summary.
    """
    try:
        current_summary = request.aesthetic_summary
        
        # 1. Refine Summary if command exists
        if request.refinement_command:
            current_summary = summarization.refine_summary(current_summary, request.refinement_command)
            
        # 2. Generate Image with gender context
        image_bytes = generation.generate_outfit_image(current_summary, request.gender)
        
        # Convert to base64 for JSON response
        import base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        return {
            "image_base64": image_b64,
            "aesthetic_summary": current_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
