from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def paginate(
    db: Session,
    query,
    page: int = 1,
    limit: int = 10,
):
    page = max(page, 1)

    limit = max(limit, 1)
    limit = min(limit, 100)

    total = db.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar_one()

    items = db.execute(
        query.offset((page - 1) * limit).limit(limit)
    ).scalars().all()

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0,
    }