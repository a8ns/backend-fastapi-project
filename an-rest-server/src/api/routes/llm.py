from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from api.dependencies import get_llm_service
from services.openai_service import OpenAIService
from services.claude_service import ClaudeService
from schemas.llm import (
    LLMRequest,
    LLMResponse,
    ProductDescriptionRequest,
    ProductNameGenerationRequest
)

router = APIRouter()


@router.post("/generate", response_model=LLMResponse)
async def generate_text(
    request: LLMRequest,
    provider: Optional[str] = Query(None, description="LLM provider to use (openai or claude)"),
    llm_service = Depends(get_llm_service)
):
    """
    Generate text using the specified LLM service with a custom prompt
    """
    try:
        result = await llm_service.generate_text(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            **(request.additional_params or {})
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")


@router.post("/product-description", response_model=LLMResponse)
async def generate_product_description(
    request: ProductDescriptionRequest,
    provider: Optional[str] = Query(None, description="LLM provider to use (openai or claude)"),
    llm_service = Depends(get_llm_service)
):
    """
    Generate a product description based on title and key points
    """
    # Build prompt for product description
    key_points_text = "\n".join([f"- {point}" for point in request.key_points])
    
    prompt = f"""
    Create a {request.length} product description for '{request.title}' with a {request.tone} tone.
    
    Include these key points:
    {key_points_text}
    
    Make the description engaging and appealing to potential customers.
    """
    
    try:
        result = await llm_service.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500 if request.length == "short" else (800 if request.length == "medium" else 1200)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating product description: {str(e)}")


@router.post("/product-name", response_model=LLMResponse)
async def generate_product_names(
    request: ProductNameGenerationRequest,
    provider: Optional[str] = Query(None, description="LLM provider to use (openai or claude)"),
    llm_service = Depends(get_llm_service)
):
    """
    Generate product name suggestions based on product attributes
    """
    features_text = "\n".join([f"- {feature}" for feature in request.features])
    
    target_audience_text = ""
    if request.target_audience:
        target_audience_text = f"\nTarget audience: {request.target_audience}"
    
    brand_style_text = ""
    if request.brand_style:
        brand_style_text = f"\nBrand style: {request.brand_style}"
    
    prompt = f"""
    Generate {request.count} creative and marketable name suggestions for a {request.product_type} with the following features:
    {features_text}
    {target_audience_text}
    {brand_style_text}
    
    For each suggestion, provide a brief explanation of why it would be effective.
    Format the output as a numbered list.
    """
    
    try:
        result = await llm_service.generate_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=800
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating product names: {str(e)}")