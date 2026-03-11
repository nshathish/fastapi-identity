from pydantic import BaseModel, Field


class ClientCreate(BaseModel):
    client_name: str = Field(min_length=1)
    redirect_uris: str = Field(
        min_length=1,
        description="Comma-separated redirect URIs.",
    )
    allowed_scopes: str = Field(default="openid profile email")
    is_public: bool = Field(default=True)


class ClientRead(BaseModel):
    id: str
    client_id: str
    client_name: str
    redirect_uris: str
    allowed_scopes: str
    is_public: bool
    is_active: bool
