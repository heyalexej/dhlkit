# Generated from an official DHL OpenAPI document. DO NOT EDIT.

from __future__ import annotations

from typing import Annotated, Literal

from dhlkit.models import DhlModel
from pydantic import AnyUrl, Field


class PostnumberRequest(DhlModel):
    firstname: Annotated[
        str,
        Field(
            description='first name',
            examples=['Max'],
            max_length=40,
            min_length=1,
            pattern="[ \\',\\-./\\\\A-Za-z_`¯µ·ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]*",
        ),
    ]
    lastname: Annotated[
        str,
        Field(
            description='last name',
            examples=['Mustermann'],
            max_length=32,
            min_length=1,
            pattern="[ \\',\\-./\\\\A-Za-z_`¯µ·ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]*",
        ),
    ]


class PostNumberResponseDetails(DhlModel):
    post_number_valid: Annotated[
        Literal[True, False],
        Field(
            alias='postNumberValid',
            description='Shows the validity of the number (true = valid,\\ \\ postnumber exists & service Packstation is active; false = not valid).',
            examples=[True],
        ),
    ]
    name_valid: Annotated[
        Literal[True, False] | None,
        Field(
            alias='nameValid',
            description='Shows the validity of the name (true = valid,\\ \\ name matches with our customer data; false = not valid).',
            examples=[True],
        ),
    ] = None


class JSONStatus(DhlModel):
    title: Annotated[str, Field(examples=['Unauthorized'])]
    status: Annotated[int, Field(examples=[401], ge=200, le=999)]
    type: Annotated[
        AnyUrl | None,
        Field(
            description='A URI reference [RFC3986] that identifies the problem type and is human-readable.',
            examples=['https://api.dhl.com/parcel/de/shipping/e0001.html'],
        ),
    ] = None
    detail: Annotated[
        str | None,
        Field(
            description='A human-readable explanation specific to this occurrence of the problem',
            examples=['Unauthorized - The client could not be authenticated.'],
            max_length=80,
            min_length=0,
        ),
    ] = None
    instance: Annotated[
        AnyUrl | None,
        Field(
            description='A URI reference that identifies the specific occurrence of the problem.',
            examples=['https://api.dhl.com/parcel/de/shipping/e0001.html'],
        ),
    ] = None


class PostnumberResponse(DhlModel):
    valid: Annotated[
        Literal[True, False],
        Field(
            description='Shows the validity of the number (true = valid, entire name matches & postnumber matches & service Packstation is active; false = not valid).',
            examples=[True],
        ),
    ]
    details: PostNumberResponseDetails | None = None
