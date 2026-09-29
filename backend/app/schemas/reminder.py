from pydantic import BaseModel


class DismissAllResponse(BaseModel):
    dismissed: int
