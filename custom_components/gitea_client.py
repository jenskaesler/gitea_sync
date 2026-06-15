"""Gitea API client for Gitea Config Sync."""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
from typing import Any

_LOGGER = logging.getLogger(__name__)


class GiteaApiError(Exception):
    """Raised when Gitea API returns an error."""


class GiteaClient:
    """Client for the Gitea REST API."""

    def __init__(self, url: str, token: str, owner: str, repo: str, branch: str) -> None:
        self._base = url.rstrip("/")
        self._token = token
        self._owner = owner
        self._repo = repo
        self._branch = branch

    def _headers(self) -> dict:
        return {
            "Authorization": f"token {self._token}",
            "Content-Type": "application/json",
        }

    def _api(self, path: str) -> str:
        return f"{self._base}/api/v1{path}"

    async def _request(self, session, method: str, path: str, **kwargs) -> Any:
        """Make an API request."""
        url = self._api(path)
        async with session.request(method, url, headers=self._headers(), **kwargs) as resp:
            if resp.status == 404:
                raise GiteaApiError(f"Not found: {path}")
            if resp.status == 401:
                raise GiteaApiError("Invalid token")
            if resp.status not in (200, 201, 204):
                text = await resp.text()
                raise GiteaApiError(f"API error {resp.status}: {text}")
            if resp.status == 204:
                return {}
            return await resp.json()

    async def test_connection(self, session) -> bool:
        """Test connection and token validity."""
        await self._request(session, "GET", f"/repos/{self._owner}/{self._repo}")
        return True

    async def get_file(self, session, path: str) -> dict | None:
        """Get a file's metadata and content from the repo."""
        try:
            return await self._request(
                session, "GET",
                f"/repos/{self._owner}/{self._repo}/contents/{path}",
                params={"ref": self._branch},
            )
        except GiteaApiError as err:
            if "Not found" in str(err):
                return None
            raise

    async def put_file(
        self,
        session,
        path: str,
        content: bytes,
        message: str,
        sha: str | None = None,
    ) -> dict:
        """Create or update a file in the repo."""
        payload: dict = {
            "message": message,
            "content": base64.b64encode(content).decode(),
            "branch": self._branch,
        }
        if sha:
            payload["sha"] = sha

        return await self._request(
            session, "POST" if sha is None else "PUT",
            f"/repos/{self._owner}/{self._repo}/contents/{path}",
            data=json.dumps(payload),
        )

    async def delete_file(self, session, path: str, sha: str, message: str) -> None:
        """Delete a file from the repo."""
        payload = {
            "message": message,
            "sha": sha,
            "branch": self._branch,
        }
        await self._request(
            session, "DELETE",
            f"/repos/{self._owner}/{self._repo}/contents/{path}",
            data=json.dumps(payload),
        )

    async def get_latest_commit(self, session) -> dict | None:
        """Get the latest commit on the branch."""
        try:
            commits = await self._request(
                session, "GET",
                f"/repos/{self._owner}/{self._repo}/commits",
                params={"sha": self._branch, "limit": 1},
            )
            return commits[0] if commits else None
        except GiteaApiError:
            return None

    @staticmethod
    def sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
