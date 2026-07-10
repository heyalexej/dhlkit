# Generated from an official DHL OpenAPI document. DO NOT EDIT.

from __future__ import annotations

from typing import Annotated

from dhlkit.models import DhlModel
from pydantic import Field


class TokenResponse(DhlModel):
    access_token: Annotated[
        str | None,
        Field(
            description='Opaque access token to be used for Bearer authentication',
            examples=['UtN71yyK8y8tuargZzmttyx8Y7Lp'],
            max_length=50,
        ),
    ] = None
    token_type: Annotated[
        str | None,
        Field(
            description="Will be set to 'Bearer'", examples=['Bearer'], max_length=20
        ),
    ] = None
    expires_in: Annotated[int | None, Field(description='Seconds', examples=[1799])] = (
        None
    )
