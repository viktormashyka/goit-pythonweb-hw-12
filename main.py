from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api import contacts, utils, auth, users


def create_app():
    app = FastAPI()
    limiter = Limiter(key_func=get_remote_address)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach the limiter to the FastAPI app
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.exception_handler(RateLimitExceeded)


    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
        )


    # Apply the rate limit to the entire app
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        response = await call_next(request)
        return response


    app.include_router(utils.router, prefix="/api")
    app.include_router(contacts.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(users.router, prefix="/api")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)