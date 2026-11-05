"""Pydaikin appliance, represent a Daikin device."""

import logging
import ssl
from uuid import uuid4

from .daikin_brp069 import DaikinBRP069

_LOGGER = logging.getLogger(__name__)


class DaikinBRP072C(DaikinBRP069):
    """Daikin class for BRP072Cxx units."""

    def __init__(  # pylint: disable=[too-many-arguments]
        self,
        device_id,
        session=None,
        *,
        key=None,
        uuid=None,
        ssl_context=None,
        fetch_optional=False,
    ) -> None:
        """Init the pydaikin appliance, representing one Daikin BRP072Cxx device.

        The uuid identifies this client to the adapter, which registers it with
        the key. Pass the same uuid each time to reuse one registration. Without
        one, a new random uuid is used, so no two installs share a uuid.
        """
        super().__init__(device_id, session, fetch_optional=fetch_optional)
        self._key = key
        if uuid is None:
            uuid = uuid4()
        self._uuid = str(uuid).replace('-', '')
        self.headers = {"X-Daikin-uuid": self._uuid}
        self.ssl_context = (
            ssl_context
            if ssl_context
            else ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        )
        self.ssl_context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        # Fixes SSL WRONG_SIGNATURE_TYPE error
        try:
            self.ssl_context.set_ciphers("DEFAULT:@SECLEVEL=0")
        except ssl.SSLError:
            # Some things won't support SECLEVEL, and the cipher setting then
            # shouldn't matter
            pass
        self.base_url = f"https://{self.device_ip}"

    async def init(self):
        """Init status."""
        await self._get_resource('common/register_terminal', {"key": self._key})
        await super().init()
