# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
"""Configuration loading for Cameo MCP per-domain servers.

Hosts:
* :class:`BridgeConfig` â€” the v2 plugin's existing token+port loader (unchanged
  behavior; reads the shared token and bound port from files written by the
  Java plugin, plus the optional ``JGS_V2_WRITE_SECRET`` env var).
* :class:`DomainConfig` â€” generic per-domain configuration consumed by
  :class:`magic_mcp_core.DomainServer`. Future per-domain plugins (v1, UAF,
  â€¦) construct one of these from their own env-var prefix.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ConfigError(RuntimeError):
    """Raised when the bridge cannot be configured."""


@dataclass(frozen=True)
class BridgeConfig:
    token: str
    port: int
    write_secret: str | None
    token_path: Path
    port_path: Path

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/v1"

    @classmethod
    def load(
        cls,
        *,
        token_path: Path | None = None,
        port_path: Path | None = None,
    ) -> BridgeConfig:
        token_path = token_path or cls.default_token_path()
        port_path = port_path or cls.default_port_path()

        if not token_path.exists():
            raise ConfigError(
                f"token file not found at {token_path}; is the Cameo plugin running?"
            )
        if not port_path.exists():
            raise ConfigError(
                f"port file not found at {port_path}; is the Cameo plugin running?"
            )

        token = token_path.read_text(encoding="utf-8").strip()
        port_raw = port_path.read_text(encoding="utf-8").strip()
        try:
            port = int(port_raw)
        except ValueError as e:
            raise ConfigError(f"port file {port_path} is not a valid integer: {port_raw!r}") from e

        write_secret = os.environ.get("JGS_V2_WRITE_SECRET") or None

        return cls(
            token=token,
            port=port,
            write_secret=write_secret,
            token_path=token_path,
            port_path=port_path,
        )

    @staticmethod
    def default_token_path() -> Path:
        base = _local_appdata()
        return base / ".magic.systems.of.systems.architect" / "2026x" / "jgs-sysmlv2-mcp.token"

    @staticmethod
    def default_port_path() -> Path:
        base = _local_appdata()
        return base / ".magic.systems.of.systems.architect" / "2026x" / "jgs-sysmlv2-mcp.port"


def _local_appdata() -> Path:
    val = os.environ.get("LOCALAPPDATA")
    if val:
        return Path(val)
    return Path.home() / ".local" / "share"


@dataclass(frozen=True)
class DomainConfig:
    """Configuration for a single per-domain MCP server.

    Each domain plugin (v2, v1, future) constructs one of these from its own
    env-var prefix (``JGS_V2_*`` for v2, ``JGS_V1_*`` for v1). Consumed by
    :class:`magic_mcp_core.DomainServer`.

    Behavior of the v2 server is currently driven by :class:`BridgeConfig`
    (loaded from disk files written by the Java plugin). ``DomainConfig`` is
    introduced for the FastMCP-based DomainServer cutover (Plan 3 Task 1+);
    it does not yet replace ``BridgeConfig`` and adding it does not change
    any existing v2 behavior.
    """

    mcp_name: str
    """The MCP server name (e.g. ``'jgs-sysmlv2'``, ``'jgs-sysmlv1'``).
    Surfaces in tools/list metadata."""

    endpoint: str
    """Base URL of the in-Cameo HttpServer (e.g. ``'http://127.0.0.1:8765/v1'``)."""

    write_token: Optional[str]
    """Secret presented to the bridge's enable-writes endpoint. ``None`` = read-only mode."""

    bearer_token: Optional[str]
    """Static bearer token for HTTP Authorization header. Used when token_file is None."""

    bearer_token_path: Optional[Path]
    """Path to the token file written by the Java plugin. Re-read on every request so
    MSOSA restarts (which rotate the token) don't require restarting the MCP process."""

    domain_id: str
    """Stable identifier for this domain (``'sysmlv2'``, ``'sysmlv1'``, ``'uaf'``, â€¦)."""

    @classmethod
    def from_env(cls, *, prefix: str, mcp_name: str, domain_id: str) -> "DomainConfig":
        """Generic env-var loader for any domain plugin.

        ``prefix`` is the env-var prefix (e.g. ``'JGS_V2'`` or ``'JGS_V1'``).
        Reads ``{prefix}_ENDPOINT`` (default ``http://127.0.0.1:8765/v1``) and
        ``{prefix}_WRITE_SECRET`` (default ``None`` = read-only mode).

        Plan 4 (v1 plugin) can add ``from_env_v1()`` by calling::

            return cls.from_env(prefix="JGS_V1", mcp_name="jgs-sysmlv1", domain_id="sysmlv1")
        """
        return cls(
            mcp_name=mcp_name,
            endpoint=os.environ.get(f"{prefix}_ENDPOINT", "http://127.0.0.1:8765/v1"),
            write_token=os.environ.get(f"{prefix}_WRITE_SECRET") or None,
            bearer_token=None,
            bearer_token_path=None,
            domain_id=domain_id,
        )

    @classmethod
    def from_env_v2(cls) -> "DomainConfig":
        """Load v2 configuration from ``JGS_V2_*`` env vars.

        Falls back to ``http://127.0.0.1:8765/v1`` if ``JGS_V2_ENDPOINT`` is
        unset (matches the bind default the Java plugin uses today). The
        write token is the existing ``JGS_V2_WRITE_SECRET`` env var that
        :class:`BridgeConfig.load` already consults.
        """
        return cls.from_env(prefix="JGS_V2", mcp_name="jgs-sysmlv2", domain_id="sysmlv2")

    @classmethod
    def from_env_v1(cls) -> "DomainConfig":
        """Load v1 configuration with file-based port/token discovery.

        Resolution order for ``endpoint``:
        1. ``JGS_V1_ENDPOINT`` env var (explicit override).
        2. Port file written by the Java plugin at
           ``%LOCALAPPDATA%/.magic.systems.of.systems.architect/2026x/jgs-sysmlv1-bridge.port``.
        3. Fallback ``http://127.0.0.1:18751/v1`` (matches plugin bind range start).

        Resolution order for ``write_token`` (the enable-writes secret):
        1. ``JGS_V1_WRITE_SECRET`` env var (the stable secret stored in the JVM env).
        2. ``JGS_V2_WRITE_SECRET`` env var (shared secret when v1 reuses v2 ClientState).
        3. ``None`` (read-only mode).

        Resolution order for ``bearer_token`` (HTTP Authorization header):
        1. ``JGS_V1_TOKEN`` env var.
        2. Token file at ``jgs-sysmlv1-bridge.token`` (rotates on each MSOSA restart).
        3. Falls back to write_token.
        """
        endpoint = os.environ.get("JGS_V1_ENDPOINT")
        if not endpoint:
            port_path = _local_appdata() / ".magic.systems.of.systems.architect" / "2026x" / "jgs-sysmlv1-bridge.port"
            if port_path.exists():
                try:
                    port = int(port_path.read_text(encoding="utf-8").strip())
                    endpoint = f"http://127.0.0.1:{port}/v1"
                except (ValueError, OSError):
                    endpoint = None
            if not endpoint:
                endpoint = "http://127.0.0.1:18751/v1"

        write_token = (
            os.environ.get("JGS_V1_WRITE_SECRET")
            or os.environ.get("JGS_V2_WRITE_SECRET")
            or None
        )

        # Static token from env (manual override — only used when token_file can't be read).
        bearer_token = os.environ.get("JGS_V1_TOKEN") or None

        # Token file rotates on every MSOSA restart; HttpClient re-reads it per-request.
        # When the endpoint specifies a non-default port, prefer the per-instance token file
        # (jgs-sysmlv1-bridge.{port}.token) so multi-instance setups use the correct token.
        base_dir = _local_appdata() / ".magic.systems.of.systems.architect" / "2026x"
        port = None
        try:
            from urllib.parse import urlparse as _urlparse
            port = _urlparse(endpoint).port
        except Exception:
            pass
        per_instance = base_dir / f"jgs-sysmlv1-bridge.{port}.token" if port else None
        generic = base_dir / "jgs-sysmlv1-bridge.token"
        if per_instance is not None and per_instance.exists():
            token_path = per_instance
        else:
            token_path = generic
        bearer_token_path: Optional[Path] = token_path if token_path.exists() else None

        return cls(
            mcp_name="jgs-sysmlv1",
            endpoint=endpoint,
            write_token=write_token,
            bearer_token=bearer_token,
            bearer_token_path=bearer_token_path,
            domain_id="sysmlv1",
        )

    @classmethod
    def from_env_dsl(cls) -> "DomainConfig":
        """Load DSL bridge configuration with file-based port/token discovery.

        Resolution order for ``endpoint``:
        1. ``JGS_DSL_ENDPOINT`` env var (explicit override).
        2. Port file written by the Java plugin at
           ``%LOCALAPPDATA%/.magic.systems.of.systems.architect/2026x/jgs-magic-dsl-bridge.port``.
        3. Fallback ``http://127.0.0.1:18761`` (BARE — no ``/v1`` suffix; HttpClient
           appends ``/v1`` internally).

        Resolution order for ``write_token``:
        1. ``JGS_DSL_WRITE_SECRET`` env var.
        2. ``None`` (read-only mode).

        Resolution order for ``bearer_token``:
        1. ``JGS_DSL_TOKEN`` env var.
        2. Token file at ``jgs-magic-dsl-bridge.token``.
        3. Falls back to ``write_token``.
        """
        endpoint = os.environ.get("JGS_DSL_ENDPOINT")
        if not endpoint:
            port_path = (
                _local_appdata()
                / ".magic.systems.of.systems.architect"
                / "2026x"
                / "jgs-magic-dsl-bridge.port"
            )
            if port_path.exists():
                try:
                    port = int(port_path.read_text(encoding="utf-8").strip())
                    endpoint = f"http://127.0.0.1:{port}"
                except (ValueError, OSError):
                    endpoint = None
            if not endpoint:
                endpoint = "http://127.0.0.1:18761"

        write_token = os.environ.get("JGS_DSL_WRITE_SECRET") or None
        bearer_token = os.environ.get("JGS_DSL_TOKEN") or None

        base_dir = (
            _local_appdata() / ".magic.systems.of.systems.architect" / "2026x"
        )
        token_file = base_dir / "jgs-magic-dsl-bridge.token"
        bearer_token_path: Optional[Path] = token_file if token_file.exists() else None

        return cls(
            mcp_name="jgs-magic-dsl",
            endpoint=endpoint,
            write_token=write_token,
            bearer_token=bearer_token,
            bearer_token_path=bearer_token_path,
            domain_id="dsl",
        )
