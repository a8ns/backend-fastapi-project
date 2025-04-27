from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from api.dependencies import get_openai_service, get_claude_service, get_llm_service
from services.openai_service import OpenAIService
from services.claude_service import ClaudeService
from schemas.llm import (
    LLMRequest,
    LLMResponse,
    ProductKeywordExtractionRequest,
    ProductDescriptionRequest,
    ProductNameGenerationRequest
)

import json

router = APIRouter()


@router.post("/extract-keywords/openai", response_model=LLMResponse)
async def extract_keywords_openai(
    request: ProductKeywordExtractionRequest,
    llm_service: OpenAIService = Depends(get_openai_service)
):
    """
    Extract product keywords from text using OpenAI
    """
    try:
        # Define the product extraction instruction
        product_extraction_prompt = """You are a product keyword extraction system. Your only task is to analyze the following text and extract relevant product information, returning ONLY a JSON object with the following possible fields:

- product: The main product mentioned (required)
- color: Any color specification for the product (if mentioned)
- size: Any size specification for the product (if mentioned)
- material: Any material specification for the product (if mentioned)
- brand: Any brand specification for the product (if mentioned)
- urgency: Whether there's an expression of urgency (if mentioned)
- quantity: Any quantity specification (if mentioned)
- style: Any style specification (if mentioned)
- pattern: Any pattern specification (if mentioned)
- gender: Any gender specification (if mentioned, e.g., "men's", "women's")
- age_group: Any age group specification (if mentioned, e.g., "kids", "adult", "senior")
- relationship: Any relationship specification (if mentioned, e.g. "friend", "boyfriend", "girlfriend", "grandfather", "mom")
- price: Any price specification (if mentioned)
- location: Any location specification (if mentioned, e.g. "near me" or city or city area e.g. "Charlottenburg")
- purpose: Any purpose specification (if mentioned, e.g. "gift")

IMPORTANT:
1. Return ONLY valid JSON without any explanations, comments, or additional text.
2. Include only fields that are explicitly mentioned in the input.
3. Do not include null or empty values.
4. Do not add quotes or formatting outside the JSON structure.
5. Keep your response concise and focus on exactly what was mentioned.

Text to analyze: {user_input}"""

        # Format the prompt with user input
        full_prompt = product_extraction_prompt.format(user_input=request.text)
        
        # Use default parameters if not provided
        model = request.model or "gpt-4o-mini-2024-07-18"
        temperature = request.temperature or 0.2
        max_tokens = request.max_tokens or 300
        
        result = await llm_service.generate_text(
            prompt=full_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        # Try to parse the JSON but keep the original LLMResponse structure
        try:
            parsed_json = json.loads(result["text"])
            # Replace the text field with the parsed JSON
            result["parsed_data"] = parsed_json
        except json.JSONDecodeError:
            # If parsing fails, add an error flag but don't break the response
            result["parsing_error"] = True
            
        return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting keywords with OpenAI: {str(e)}")

@router.post("/extract-keywords/claude", response_model=LLMResponse)
async def extract_keywords_claude(
    request: ProductKeywordExtractionRequest,
    llm_service: ClaudeService = Depends(get_claude_service)
):
    """
    Extract product keywords from text using Claude
    """
    try:
        # Define the product extraction instruction
        product_extraction_prompt = """You are a product keyword extraction system. Your only task is to analyze the following text and extract relevant product information, returning ONLY a JSON object with the following possible fields:

- product: The main product mentioned (required)
- color: Any color specification for the product (if mentioned)
- size: Any size specification for the product (if mentioned)
- material: Any material specification for the product (if mentioned)
- brand: Any brand specification for the product (if mentioned)
- urgency: Whether there's an expression of urgency (if mentioned)
- quantity: Any quantity specification (if mentioned)
- style: Any style specification (if mentioned)
- pattern: Any pattern specification (if mentioned)
- gender: Any gender specification (if mentioned, e.g., "men's", "women's")
- age_group: Any age group specification (if mentioned, e.g., "kids", "adult")

IMPORTANT:
1. Return ONLY valid JSON without any explanations, comments, or additional text.
2. Include only fields that are explicitly mentioned in the input.
3. Do not include null or empty values.
4. Do not add quotes or formatting outside the JSON structure.
5. Keep your response concise and focus on exactly what was mentioned.

Text to analyze: {user_input}"""

        # Format the prompt with user input
        full_prompt = product_extraction_prompt.format(user_input=request.text)
        
        # Use default parameters if not provided
        model = request.model or "claude-3-sonnet-20240229"
        temperature = request.temperature or 0.2
        max_tokens = request.max_tokens or 300
        
        result = await llm_service.generate_text(
            prompt=full_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting keywords with Claude: {str(e)}")

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