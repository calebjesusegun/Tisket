from pydantic import BaseModel, ConfigDict, Field


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TagWithCounts(TagRead):
    task_count: int
    note_count: int


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60, examples=["work"])


class TagUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=60, examples=["personal"])
