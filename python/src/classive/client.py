"""Synchronous and asynchronous public clients."""
from __future__ import annotations
import httpx
from .transport import Transport
from .async_transport import AsyncTransport
from . import resources, async_resources

class Classive:
    """REST client. Defaults to CLASSIVE_API_KEY; use as a context manager to close pooled connections."""
    def __init__(self, api_key: str | None = None, *, base_url: str = "https://api.classive.app", timeout: float = 30,
                 max_retries: int = 2, http_client: httpx.Client | None = None):
        self._transport = Transport(api_key, base_url=base_url, timeout=timeout, max_retries=max_retries, http_client=http_client)
        self.jobs = resources.Jobs(self._transport)
        self.materials = resources.Materials(self._transport)
        self.files = resources.Files(self._transport)
        self.voices = resources.Voices(self._transport)
        self.preferences = resources.Preferences(self._transport)
        self.prices = resources.Prices(self._transport)
        self.keys = resources.Keys(self._transport)
        self.webhooks = resources.Webhooks(self._transport)
        self.billing = resources.Billing(self._transport)
        self.quotes = resources.Quotes(self._transport)
        self.curricula = resources.Curricula(self._transport)
        self.organisation = resources.Organisation(self._transport)

    def close(self) -> None: self._transport.close()
    def __enter__(self) -> Classive: return self
    def __exit__(self, *args) -> None: self.close()

class AsyncClassive:
    """Native asynchronous REST client. Use async with; asyncio cancellation never cancels a server job."""
    def __init__(self, api_key: str | None = None, *, base_url: str = "https://api.classive.app", timeout: float = 30,
                 max_retries: int = 2, http_client: httpx.AsyncClient | None = None):
        self._transport = AsyncTransport(api_key, base_url=base_url, timeout=timeout, max_retries=max_retries, http_client=http_client)
        self.jobs = async_resources.Jobs(self._transport)
        self.materials = async_resources.Materials(self._transport)
        self.files = async_resources.Files(self._transport)
        self.voices = async_resources.Voices(self._transport)
        self.preferences = async_resources.Preferences(self._transport)
        self.prices = async_resources.Prices(self._transport)
        self.keys = async_resources.Keys(self._transport)
        self.webhooks = async_resources.Webhooks(self._transport)
        self.billing = async_resources.Billing(self._transport)
        self.quotes = async_resources.Quotes(self._transport)
        self.curricula = async_resources.Curricula(self._transport)
        self.organisation = async_resources.Organisation(self._transport)

    async def close(self) -> None: await self._transport.close()
    async def __aenter__(self) -> AsyncClassive: return self
    async def __aexit__(self, *args) -> None: await self.close()
