from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class DhlModel(BaseModel):
    """Base for hand-written DHL JSON models.

    Python uses snake_case while serialization follows DHL's camelCase wire names.
    Unknown fields are rejected so gateway changes become visible during development.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )
