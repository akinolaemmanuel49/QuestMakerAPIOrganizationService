from fastapi import FastAPI

from core.api.endpoints.organization import organization

app = FastAPI()

# Register routers
app.include_router(router=organization, tags=[
                   'Organizations'], prefix='/organizations')
