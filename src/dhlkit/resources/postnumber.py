from __future__ import annotations

from dhlkit.generated.models.postnumber import PostnumberRequest, PostnumberResponse
from dhlkit.resource import AsyncResource, Resource


class PostnumberResource(Resource):
    """Parcel DE Postnumber v1 using ROPC Bearer auth (``docs/AUTH.md``)."""

    def verify(self, postnumber: str | int, *, firstname: str, lastname: str) -> PostnumberResponse:
        """Verify a postnumber with a Bearer-authenticated ``POST``; see ``docs/AUTH.md``."""
        body = PostnumberRequest(firstname=firstname, lastname=lastname)
        # POST, not GET — GET returns a misleading 401 (verified 2026-07-09).
        return self._request(
            "postnumber.verify",
            "POST",
            "/customers/{postnumber}",
            path_params={"postnumber": postnumber},
            body=body,
            response_model=PostnumberResponse,
            accepted_statuses={200, 412},
        )


class AsyncPostnumberResource(AsyncResource):
    """Asynchronous Parcel DE Postnumber v1 resource."""

    async def verify(
        self,
        postnumber: str | int,
        *,
        firstname: str,
        lastname: str,
    ) -> PostnumberResponse:
        body = PostnumberRequest(firstname=firstname, lastname=lastname)
        # POST, not GET — GET returns a misleading 401 (verified 2026-07-09).
        return await self._request(
            "postnumber.verify",
            "POST",
            "/customers/{postnumber}",
            path_params={"postnumber": postnumber},
            body=body,
            response_model=PostnumberResponse,
            accepted_statuses={200, 412},
        )
