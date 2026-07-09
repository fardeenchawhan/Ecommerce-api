import secrets
import string


def generate_random_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


def generate_sku(
    category_name: str,
    brand: str,
) -> str:
    category_part = (
        category_name[:3]
        .upper()
        .replace(" ", "")
    )

    brand_part = (
        brand[:8]
        .upper()
        .replace(" ", "")
    )

    random_part = generate_random_code()

    return f"{category_part}-{brand_part}-{random_part}"