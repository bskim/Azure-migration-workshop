from threading import Lock
from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, StringConstraints

MAX_ITEMS = 100


class ItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Annotated[
        str,
        StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=80),
    ]


class Item(ItemInput):
    id: int


def create_app() -> FastAPI:
    application = FastAPI(title="Azure Migration Workshop", version="0.1.0")
    items = [
        Item(id=1, name="sample-one"),
        Item(id=2, name="sample-two"),
    ]
    lock = Lock()

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/items", response_model=list[Item])
    def list_items() -> list[Item]:
        with lock:
            return list(items)

    @application.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
    def add_item(payload: ItemInput) -> Item:
        with lock:
            if len(items) >= MAX_ITEMS:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Workshop item limit reached.",
                )
            item = Item(id=len(items) + 1, name=payload.name)
            items.append(item)
            return item

    return application


app = create_app()
