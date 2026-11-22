import re

from pydantic import AnyHttpUrl, BaseModel, TypeAdapter, ValidationError, field_validator

LINK_PATTERN = re.compile(r"https?://\S+")
_url_checker = TypeAdapter(AnyHttpUrl)


class PostingRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def check_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message must not be empty")
        if len(v) > 200:
            raise ValueError("Message must not exceed 200 characters")
        links = LINK_PATTERN.findall(v)
        if len(links) != 1:
            raise ValueError(
                "Message must contain exactly one link starting with http:// or https://"
            )
        try:
            _url_checker.validate_python(links[0].rstrip(".,!?;:)"))
        except ValidationError:
            raise ValueError("The link is not a valid URL")
        return v


class PlatformResult(BaseModel):
    platform: str
    status: str  # "success" or "failed"
    posted_url: str | None = None
    public_access: bool = False
    date: str | None = None
    time: str | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool  # true if at least one platform succeeded
    results: list[PlatformResult]