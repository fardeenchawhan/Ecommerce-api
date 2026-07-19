import logging
import sys
import time

from fastapi import Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("ecommerce-api")


class LoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        start = time.perf_counter()

        try:
            response = await call_next(request)

        except Exception:
            logger.exception(
                "Unhandled exception while processing %s %s",
                request.method,
                request.url.path,
            )
            raise

        duration = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s | %s | %.2f ms",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        return response