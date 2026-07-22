import json

from sqlalchemy import select

from src.ai.schemas import ProductMetadataSchema
from src.ai.prompts import build_product_metadata_prompt
from src.ai.service import client
from src.category.models import CategoryModel
from src.utils.settings import settings
from src.cache.service import get_cache, set_cache
from fastapi.encoders import jsonable_encoder

AI_METADATA_CACHE = 60 * 60 * 24

def generate_product_metadata(
    db,
    name: str,
    description: str,
    brand: str | None,
):
    
    cache_key = f"ai:metadata:{name}:{brand}"

    cached = get_cache(cache_key)

    if cached:
        return ProductMetadataSchema(**cached)
    
    categories = (
        db.execute(
            select(CategoryModel.name)
        )
        .scalars()
        .all()
    )

    prompt = build_product_metadata_prompt(categories)

    user_prompt = f"""
Name: {name}

Brand: {brand}

Description:

{description}
"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        temperature=0,
        response_format={
            "type": "json_object",
        },
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    data = json.loads(
        response.choices[0].message.content
    )

    category = (
    db.execute(
        select(CategoryModel).where(
            CategoryModel.name == data["category"]
        )
    )
    .scalar_one_or_none()
)

    if category is None:
        raise ValueError(
            f"Unknown category returned by AI: {data['category']}"
        )

    data["category_id"] = category.id

    metadata = ProductMetadataSchema(**data)

    set_cache(
        cache_key,
        jsonable_encoder(metadata),
        AI_METADATA_CACHE,
    )

    return metadata