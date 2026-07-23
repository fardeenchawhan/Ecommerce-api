import json

from groq import Groq
from src.ai.schemas import ProductSearchFilterSchema
from src.utils.settings import settings
from sqlalchemy import select

from src.category.models import CategoryModel
from src.ai.prompts import build_prompt,build_fallback_prompt

client = Groq(
    api_key=settings.GROQ_API_KEY,
)



def parse_search_query(
    db,
    query: str,
):
    

    categories = (
        db.execute(
            select(CategoryModel.name)
        )
        .scalars()
        .all()
    )

    system_prompt = build_prompt(categories)

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        response_format={
            "type": "json_object",
        },
    )

    content = response.choices[0].message.content

    data = json.loads(content)

    return ProductSearchFilterSchema(**data)



def rewrite_search(query: str) -> str:

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": build_fallback_prompt(),
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )

    return response.choices[0].message.content.strip()