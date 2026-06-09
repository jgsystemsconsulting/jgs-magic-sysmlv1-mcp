# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
#
# This file is part of magic-development, proprietary software of
# JG Systems Consulting Ltd. Unauthorized copying, modification,
# distribution, reverse engineering, or use of this file, via any
# medium, is strictly prohibited without a valid written licence
# from JG Systems Consulting Ltd. See LICENSE at the repository
# root for the full terms.
#
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary

"""Thin async HTTP client wrapping httpx, configured from BridgeConfig."""
from __future__ import annotations

from typing import Any

import httpx

from .config import BridgeConfig
from .errors import BridgeError, problem_to_exception


def _paginate_envelope(
    raw: dict[str, Any], list_key: str, *, limit: int, offset: int
) -> dict[str, Any]:
    """Normalise a list-returning endpoint response into a paginated envelope.

    Works in two modes:

    * **Native pagination:** if the plugin already honoured ``limit``/``offset``
      and returned ``has_more`` + ``total_matched`` in the envelope, we keep
      them as-is.
    * **Client-side slicing:** older plugin builds return the whole list. We
      slice it here so callers always see the same envelope regardless of
      which plugin version is on the other end.

    :param raw: Parsed plugin response. Expected to contain the item list
        under ``list_key`` (``"results"`` for find_by_*, ``"children"`` for
        list_children).
    :param list_key: Key in ``raw`` that holds the item list.
    :param limit: Caller-requested page size. ``<= 0`` disables slicing.
    :param offset: Caller-requested starting index.
    :returns: A dict with ``results``, ``has_more`` (bool), ``total_matched``
        (int), and any non-list metadata fields from ``raw`` (e.g.
        ``parentId``) preserved unchanged.
    """
    items = raw.get(list_key, [])
    if not isinstance(items, list):
        return raw

    # Native pagination: plugin already sliced and reported has_more.
    if "has_more" in raw and "total_matched" in raw:
        envelope = dict(raw)
        envelope["results"] = envelope.pop(list_key, items)
        return envelope

    # Client-side slicing. Preserve non-list metadata (e.g. parentId).
    total = len(items)
    start = max(0, offset)
    end = total if limit is None or limit <= 0 else start + limit
    sliced = items[start:end]

    envelope: dict[str, Any] = {k: v for k, v in raw.items() if k != list_key}
    envelope["results"] = sliced
    envelope["total_matched"] = total
    envelope["has_more"] = end < total
    return envelope


#: Templates whose output is immutable for the lifetime of the client —
#: they describe the Cameo standard libraries (ISQ, SI, ScalarValues, …),
#: which do not change during a session. Cached in
#: :attr:`BridgeHttpClient._library_cache` on first call; served from cache
#: on every subsequent call.
_LIBRARY_TEMPLATES: frozenset[str] = frozenset({
    "list_standard_libraries",
    "find_library_type",
})


class _RetryingClient:
    """Thin proxy around httpx.AsyncClient that auto-reconnects on 401.

    Wraps every HTTP method (get, post, patch, delete, request). On a 401
    response it calls back to the owning BridgeHttpClient to reload credentials
    from disk, then retries the original request exactly once. This means every
    call site in BridgeHttpClient continues to use ``self._client.get(...)``
    unchanged — the retry logic lives entirely here.
    """

    def __init__(self, owner: "BridgeHttpClient", inner: httpx.AsyncClient) -> None:
        self._owner = owner
        self._inner = inner

    async def _call(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        resp = await self._inner.request(method, url, **kwargs)
        if resp.status_code == 401 and not self._owner._reconnecting:
            self._owner._reconnecting = True
            try:
                await self._owner._reconnect()
            finally:
                self._owner._reconnecting = False
            # After _reconnect, self._owner._client is the new _RetryingClient.
            resp = await self._owner._client._inner.request(method, url, **kwargs)
        return resp

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._call("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._call("POST", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._call("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._call("DELETE", url, **kwargs)

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        return await self._call(method, url, **kwargs)

    async def aclose(self) -> None:
        await self._inner.aclose()


class BridgeHttpClient:
    """Async HTTP client for the Cameo bridge plugin."""

    def __init__(self, config: BridgeConfig, *, timeout_seconds: float = 30.0) -> None:
        self._config = config
        self._timeout_seconds = timeout_seconds
        # Caches declared before _make_client so the event_hooks can reference them.
        self._library_cache: dict[tuple, dict[str, Any]] = {}
        self._slow_template_cache: dict[tuple, dict[str, Any]] = {}
        self._reconnecting = False  # guard against recursive retries
        self._client = self._make_client(config, timeout_seconds)

    def _make_client(self, config: BridgeConfig, timeout_seconds: float) -> "_RetryingClient":
        inner = httpx.AsyncClient(
            base_url=config.base_url,
            headers={"Authorization": f"Bearer {config.token}"},
            timeout=timeout_seconds,
            event_hooks={"request": [self._on_request]},
        )
        return _RetryingClient(self, inner)

    async def _reconnect(self) -> None:
        """Re-read token+port from disk and rebuild the httpx client.

        Called automatically on a 401 response (Cameo restarted with a new
        token). Swaps the client in-place so all subsequent requests use the
        fresh credentials without requiring a manual MCP reconnect.
        """
        old_client = self._client
        self._config = BridgeConfig.load(
            token_path=self._config.token_path,
            port_path=self._config.port_path,
        )
        self._client = self._make_client(self._config, self._timeout_seconds)
        # Clear caches — the new session may have a different model state.
        self._library_cache.clear()
        self._slow_template_cache.clear()
        await old_client._inner.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    def _clear_library_cache(self) -> None:
        """Drop all cached standard-library responses.

        Safe to call at any time; the next library query rebuilds the cache.
        Intended for tests and for rare cases where a library was imported
        into the project mid-session.
        """
        self._library_cache.clear()

    def _invalidate_slow_cache(self) -> None:
        """Drop all cached slow-template responses.

        Called by :meth:`_on_request` on every non-GET HTTP request.
        Exposed as a method so tests and rare external callers can force a
        refetch.
        """
        self._slow_template_cache.clear()

    async def _on_request(self, request: httpx.Request) -> None:
        """httpx request hook: invalidate the slow-template cache on writes.

        Fires for every outgoing request (any method, any URL). The rule:

        * GET requests never invalidate.
        * POSTs to the template endpoint invalidate **only** if the template
          being executed is neither a slow (read-tier) template nor a
          library (read-tier) template. Read-template POSTs are exempted
          so a fresh audit run doesn't wipe cached entries from a
          previous, unrelated audit template.
        * POSTs to any other endpoint, DELETEs, PUTs, and PATCHes are
          assumed to mutate the model and do invalidate. This is the
          safety net that catches ``create_element``, ``save_project``,
          ``commit_batch``, ``execute_groovy``, and any other writer
          without having to instrument each call site individually.

        Cache hits in :meth:`execute_template` short-circuit before reaching
        the HTTP layer, so they never trigger this hook.
        """
        if request.method == "GET":
            return

        # Inspect template-endpoint POSTs; exempt read-tier template calls.
        if request.url.path.endswith("/macros/execute-template"):
            try:
                body = request.content
                if body:
                    import json as _json
                    payload = _json.loads(body)
                    template = payload.get("template", "")
                    if template in self._SLOW_TEMPLATES or template in _LIBRARY_TEMPLATES:
                        return
            except (ValueError, TypeError):
                # If we can't parse the body (unexpected), fall through to
                # the safe default: invalidate.
                pass

        self._invalidate_slow_cache()


    # -------------------------------------------------------------------------
    # Lifecycle / info
    # -------------------------------------------------------------------------

    async def ping(self) -> dict[str, Any]:
        try:
            resp = await self._client.get("/ping")
        except httpx.ConnectError as ce:
            raise BridgeError({
                "type": "https://jgs-sysmlv2-mcp/errors/plugin-not-running",
                "title": "Plugin not running",
                "status": 503,
                "detail": f"could not connect to bridge at {self._config.base_url}: {ce}",
            }) from ce
        return self._check_and_parse(resp)

    async def get_plugin_info(self) -> dict[str, Any]:
        resp = await self._client.get("/plugin/info")
        return self._check_and_parse(resp)

    # -------------------------------------------------------------------------
    # Read operations
    # -------------------------------------------------------------------------

    async def get_element(self, element_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"/elements/{element_id}")
        return self._check_and_parse(resp)

    async def list_children(
        self, parent_id: str, *, limit: int = 200, offset: int = 0
    ) -> dict[str, Any]:
        resp = await self._client.get(
            f"/elements/{parent_id}/children",
            params={"limit": limit, "offset": offset},
        )
        raw = self._check_and_parse(resp)
        return _paginate_envelope(raw, "children", limit=limit, offset=offset)

    async def find_by_name(
        self, name: str, *, limit: int = 200, offset: int = 0
    ) -> dict[str, Any]:
        resp = await self._client.get(
            "/elements/by-name",
            params={"name": name, "limit": limit, "offset": offset},
        )
        raw = self._check_and_parse(resp)
        return _paginate_envelope(raw, "results", limit=limit, offset=offset)

    async def find_by_type(
        self, type_name: str, *, limit: int = 200, offset: int = 0
    ) -> dict[str, Any]:
        resp = await self._client.get(
            "/elements/by-type",
            params={"type": type_name, "limit": limit, "offset": offset},
        )
        raw = self._check_and_parse(resp)
        return _paginate_envelope(raw, "results", limit=limit, offset=offset)

    async def describe_element(self, element_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"/elements/{element_id}/describe")
        return self._check_and_parse(resp)

    async def get_element_structure(self, element_id: str) -> dict[str, Any]:
        """GET /v1/elements/{id}/structure — compact structural JSON.

        Returns typing, specialization, redefinition, subsetting,
        multiplicity, documentation snippet, and owned-element counts for
        one element in a single call. Intended as a cheap alternative to
        ``get_sysml_text`` when the caller needs to explore or verify
        structure, not export the full textual notation.
        """
        resp = await self._client.get(f"/elements/{element_id}/structure")
        return self._check_and_parse(resp)

    async def get_root_package_id(self) -> dict[str, Any]:
        resp = await self._client.get("/elements/root-package")
        return self._check_and_parse(resp)

    async def get_qualified_name(self, element_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"/elements/{element_id}/qualified-name")
        return self._check_and_parse(resp)

    async def walk_tree(
        self,
        root_id: str,
        depth: int = 3,
        max_elements: int = 500,
        children_per_node: int = 50,
    ) -> dict[str, Any]:
        # R3-01 fix: forward pagination caps so large trees don't overflow the
        # MCP client's 25K token response cap. Backend emits truncation markers.
        resp = await self._client.get(
            f"/elements/{root_id}/tree",
            params={
                "depth": depth,
                "max_elements": max_elements,
                "children_per_node": children_per_node,
            },
        )
        return self._check_and_parse(resp)

    async def find_by_qualified_name(self, qualified_name: str) -> dict[str, Any]:
        resp = await self._client.get("/elements/by-qualified-name", params={"name": qualified_name})
        return self._check_and_parse(resp)

    async def get_standard_library_types(self) -> dict[str, Any]:
        """GET /v1/standard-library — returns curated standard library type list.

        Response is immutable for the client's lifetime; cached in
        :attr:`_library_cache` after the first call.
        """
        cache_key = ("get_standard_library_types",)
        if cache_key in self._library_cache:
            return self._library_cache[cache_key]
        resp = await self._client.get("/standard-library")
        result = self._check_and_parse(resp)
        self._library_cache[cache_key] = result
        return result

    async def get_relationships(self, element_id: str) -> dict[str, Any]:
        """GET /v1/elements/{id}/relationships — outgoing + incoming relationships."""
        resp = await self._client.get(f"/elements/{element_id}/relationships")
        return self._check_and_parse(resp)

    async def search(self, query: str, max_results: int = 50) -> dict[str, Any]:
        """GET /v1/search?q=...&max=N — fuzzy name search over user model elements."""
        resp = await self._client.get("/search", params={"q": query, "max": max_results})
        return self._check_and_parse(resp)

    # -------------------------------------------------------------------------
    # Write operations
    # -------------------------------------------------------------------------

    async def create_element(self, endpoint: str, parent_id: str, name: str) -> dict[str, Any]:
        """POST to /elements/{endpoint} with parentId and name."""
        resp = await self._client.post(
            f"/elements/{endpoint}",
            json={"parentId": parent_id, "name": name},
        )
        return self._check_and_parse(resp)

    async def create_element_by_type(self, parent_id: str, name: str, type_name: str) -> dict[str, Any]:
        """POST to /v1/elements with parentId, name, and type."""
        resp = await self._client.post(
            "/elements",
            json={"parentId": parent_id, "name": name, "type": type_name},
        )
        return self._check_and_parse(resp)

    async def list_element_types(self) -> dict[str, Any]:
        """GET /v1/element-types — returns all creatable SysML/KerML types."""
        resp = await self._client.get("/element-types")
        return self._check_and_parse(resp)

    async def save_project(self, comment: str | None = None) -> dict[str, Any]:
        """POST /v1/project/save — saves the current open project.

        S-18-1 fix (2026-04-14): Cameo's ProjectsManager.saveProject is
        synchronous and can take 60-120s on a large project, blocking the
        Undertow response thread until the disk write finishes. The default
        30s client timeout is too short. Override to 180s for this call.

        If *comment* is provided and non-blank, it is forwarded to the plugin
        so ESI/Teamwork Cloud projects can commit with the given message,
        bypassing the "Save as New Version" modal dialog.
        """
        kwargs: dict = {"timeout": 180.0}
        if comment:
            import json as _json
            kwargs["content"] = _json.dumps({"comment": comment}).encode()
            kwargs["headers"] = {"Content-Type": "application/json"}
        resp = await self._client.post("/project/save", **kwargs)
        return self._check_and_parse(resp)

    async def execute_groovy(self, script: str) -> dict[str, Any]:
        """POST /v1/macros/execute — run arbitrary Groovy in Cameo's JVM.

        Requires dev mode to be active on the plugin side. Called only by
        the jgs-sysmlv2-groovy-escape skill via the ``execute_groovy`` MCP
        tool; built-in tools use :meth:`execute_template` instead.
        """
        resp = await self._client.post(
            "/macros/execute",
            json={"script": script},
        )
        return self._check_and_parse(resp)

    #: Templates that walk the entire project and grow linearly with model
    #: size. See S-13-1 in docs/SKILL-ISSUE-REGISTER.md — on a 787-element
    #: project these can take 30-60s, exceeding the default 30s timeout.
    _SLOW_TEMPLATES: frozenset[str] = frozenset({
        "impact_analysis",
        "validate_model",
        "generate_model_summary",
        "check_requirement_coverage",
        "find_unused_definitions",
        "check_documentation_coverage",
        "check_naming_conventions",
        "find_duplicates",
        "export_requirements_matrix",
        "get_model_metrics",
    })

    async def execute_template(
        self, template: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """POST /v1/macros/execute-template — run a registered script template.

        The plugin looks up ``template`` in its ScriptTemplateRegistry, checks
        the session's tier against the template's declared tier, validates
        ``params`` against the template's parameter contract, binds the
        validated values into a fresh Groovy ScriptEngine, and evaluates the
        template body.

        Introduced in the v3 template library refactor
        (docs/architecture/template-library-design.md). All 72 built-in
        scripted tools route through this method instead of
        :meth:`execute_groovy`.

        S-13-1 fix (2026-04-14): Templates in :attr:`_SLOW_TEMPLATES` walk
        the entire project and scale linearly with model size. The default
        30s client timeout is too short once the project exceeds ~500
        elements. Bump to 180s for those templates only.

        Library templates in :data:`_LIBRARY_TEMPLATES` describe the Cameo
        standard libraries, which are immutable for the client's lifetime;
        their responses are cached in :attr:`_library_cache`.

        Slow templates in :attr:`_SLOW_TEMPLATES` walk the entire project;
        their responses are cached in :attr:`_slow_template_cache` and
        invalidated on any non-GET request the client issues. Cache hits
        short-circuit before the HTTP layer, so hitting the cache does NOT
        trigger the request-hook invalidation.
        """
        params_key = tuple(sorted(params.items()))

        # Library templates are immutable — serve from cache on repeat calls.
        if template in _LIBRARY_TEMPLATES:
            library_key = (template, params_key)
            if library_key in self._library_cache:
                return self._library_cache[library_key]

        # Slow templates are cached until the next write.
        if template in self._SLOW_TEMPLATES:
            slow_key = (template, params_key)
            if slow_key in self._slow_template_cache:
                return self._slow_template_cache[slow_key]

        kwargs: dict[str, Any] = {
            "json": {"template": template, "params": params},
        }
        if template in self._SLOW_TEMPLATES:
            kwargs["timeout"] = 180.0
        resp = await self._client.post("/macros/execute-template", **kwargs)
        result = self._check_and_parse(resp)

        # Re-check membership AFTER the request — the _on_request hook just
        # fired and may have cleared the cache. We still want to repopulate
        # with the fresh result we just obtained.
        if template in _LIBRARY_TEMPLATES:
            self._library_cache[(template, params_key)] = result
        if template in self._SLOW_TEMPLATES:
            self._slow_template_cache[(template, params_key)] = result
        return result

    async def get_macros_health(self) -> dict[str, Any]:
        """GET /v1/macros/health — template registry load diagnostics.

        Returns ``{loaded, failed, warned, failures, warnings}``. Useful for
        startup health checks: if ``failed > 0`` the MCP server should
        surface the failure list as a setup error.
        """
        resp = await self._client.get("/macros/health")
        return self._check_and_parse(resp)

    async def enable_dev_mode(self, secret: str) -> dict[str, Any]:
        """POST /v1/safety/enable-dev-mode — enable raw Groovy execution.

        Dev mode is orthogonal to tier: a READ-tier session can enable dev
        mode to run custom read-only scripts. Requires the
        ``JGS_V2_DEV_SECRET`` env var to be set on the plugin side, and
        the caller must present that secret.
        """
        resp = await self._client.post(
            "/safety/enable-dev-mode",
            json={"secret": secret},
        )
        return self._check_and_parse(resp)

    async def disable_dev_mode(self) -> dict[str, Any]:
        """POST /v1/safety/disable-dev-mode — disable raw Groovy execution."""
        resp = await self._client.post("/safety/disable-dev-mode")
        return self._check_and_parse(resp)

    async def rename_element(self, element_id: str, name: str) -> dict[str, Any]:
        resp = await self._client.patch(
            f"/elements/{element_id}",
            json={"name": name},
        )
        return self._check_and_parse(resp)

    async def set_documentation(self, element_id: str, documentation: str) -> dict[str, Any]:
        resp = await self._client.patch(
            f"/elements/{element_id}",
            json={"documentation": documentation},
        )
        return self._check_and_parse(resp)

    async def delete_element(self, element_id: str) -> None:
        resp = await self._client.delete(f"/elements/{element_id}")
        if resp.status_code == 204:
            return
        # Any non-204 is an error
        self._check_and_parse(resp)

    async def move_element(self, element_id: str, new_parent_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{element_id}/move",
            json={"newParentId": new_parent_id},
        )
        return self._check_and_parse(resp)

    # -------------------------------------------------------------------------
    # Diagram operations
    # -------------------------------------------------------------------------

    async def list_diagram_kinds(self) -> dict[str, Any]:
        resp = await self._client.get("/diagrams/kinds")
        return self._check_and_parse(resp)

    async def create_diagram(self, parent_id: str, name: str, kind: str) -> dict[str, Any]:
        resp = await self._client.post(
            "/diagrams",
            json={"parentId": parent_id, "name": name, "kind": kind},
        )
        return self._check_and_parse(resp)

    async def list_diagrams(self, parent_id: str | None = None) -> dict[str, Any]:
        params = {}
        if parent_id is not None:
            params["parentId"] = parent_id
        resp = await self._client.get("/diagrams", params=params)
        return self._check_and_parse(resp)

    # -------------------------------------------------------------------------
    # Batch control operations
    # -------------------------------------------------------------------------

    async def begin_batch(self, name: str) -> dict[str, Any]:
        resp = await self._client.post(
            "/batch/begin",
            json={"name": name},
        )
        return self._check_and_parse(resp)

    async def commit_batch(self, batch_id: str) -> dict[str, Any]:
        resp = await self._client.post(f"/batch/{batch_id}/commit")
        return self._check_and_parse(resp)

    async def abort_batch(self, batch_id: str) -> dict[str, Any]:
        resp = await self._client.post(f"/batch/{batch_id}/abort")
        return self._check_and_parse(resp)

    # -------------------------------------------------------------------------
    # Specialization / typing operations
    # -------------------------------------------------------------------------

    async def specialize(self, child_id: str, parent_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{child_id}/specialize",
            json={"parentId": parent_id},
        )
        return self._check_and_parse(resp)

    async def set_type(self, feature_id: str, type_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{feature_id}/type",
            json={"typeId": type_id},
        )
        return self._check_and_parse(resp)

    # -------------------------------------------------------------------------
    # Traceability operations
    # -------------------------------------------------------------------------

    async def add_satisfy(self, element_id: str, requirement_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{element_id}/satisfy",
            json={"requirementId": requirement_id},
        )
        return self._check_and_parse(resp)

    async def add_verify(self, element_id: str, requirement_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{element_id}/verify",
            json={"requirementId": requirement_id},
        )
        return self._check_and_parse(resp)

    async def add_derive(self, derived_id: str, source_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{derived_id}/derive",
            json={"sourceId": source_id},
        )
        return self._check_and_parse(resp)

    # --- A2 migrated relationship/membership mutators (compiled-Java handlers) ---

    async def add_framed_concern(self, parent_id: str, concern_name: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{parent_id}/framed-concern",
            json={"concernName": concern_name},
        )
        return self._check_and_parse(resp)

    async def add_subsetting(self, subsetting_id: str, subsetted_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{subsetting_id}/subsetting",
            json={"subsettedId": subsetted_id},
        )
        return self._check_and_parse(resp)

    async def add_redefinition(self, redefining_id: str, redefined_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{redefining_id}/redefinition",
            json={"redefinedId": redefined_id},
        )
        return self._check_and_parse(resp)

    async def add_conjugation(self, conjugated_type_id: str, original_type_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{conjugated_type_id}/conjugation",
            json={"originalTypeId": original_type_id},
        )
        return self._check_and_parse(resp)

    async def add_stakeholder(self, parent_id: str, stakeholder_name: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{parent_id}/stakeholder",
            json={"stakeholderName": stakeholder_name},
        )
        return self._check_and_parse(resp)

    async def add_variant(
        self, variation_point_id: str, variant_name: str, variant_type: str | None = None
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"variantName": variant_name}
        if variant_type:
            body["variantType"] = variant_type
        resp = await self._client.post(
            f"/elements/{variation_point_id}/variant",
            json=body,
        )
        return self._check_and_parse(resp)

    async def add_succession(self, parent_id: str, source_id: str, target_id: str) -> dict[str, Any]:
        resp = await self._client.post(
            f"/elements/{parent_id}/succession",
            json={"sourceId": source_id, "targetId": target_id},
        )
        return self._check_and_parse(resp)

    async def set_value(self, element_id: str, value: Any) -> dict[str, Any]:
        """POST /v1/elements/{id}/value — set a default value on a feature."""
        resp = await self._client.post(
            f"/elements/{element_id}/value",
            json={"value": value},
        )
        return self._check_and_parse(resp)

    async def set_connection_ends(self, connection_id: str, source_end_id: str, target_end_id: str) -> dict[str, Any]:
        """POST /v1/elements/{id}/connection-ends — wire up connection endpoints.

        S-06-3 fix (2026-04-14): setting connection ends triggers Cameo's
        resource-set update notification chain which is synchronous and can
        take >30s on non-trivial models. The work always commits but the
        HTTP response blocks the Undertow thread until notification fan-out
        finishes. Override timeout to 120s.
        """
        resp = await self._client.post(
            f"/elements/{connection_id}/connection-ends",
            json={"sourceEndId": source_end_id, "targetEndId": target_end_id},
            timeout=120.0,
        )
        return self._check_and_parse(resp)

    async def set_multiplicity(self, feature_id: str, lower: int, upper: int) -> dict[str, Any]:
        """POST /v1/elements/{id}/multiplicity — set multiplicity range."""
        resp = await self._client.post(
            f"/elements/{feature_id}/multiplicity",
            json={"lower": lower, "upper": upper},
        )
        return self._check_and_parse(resp)

    async def set_requirement_text(self, element_id: str, text: str) -> dict[str, Any]:
        """POST /v1/elements/{id}/requirement-text — set requirement text."""
        resp = await self._client.post(
            f"/elements/{element_id}/requirement-text",
            json={"text": text},
        )
        return self._check_and_parse(resp)

    async def set_constraint(self, parent_id: str, name: str, expression: str, language: str = "SysML") -> dict[str, Any]:
        """POST /v1/elements/{id}/constraint — add a constraint expression."""
        resp = await self._client.post(
            f"/elements/{parent_id}/constraint",
            json={"name": name, "expression": expression, "language": language},
        )
        return self._check_and_parse(resp)

    async def create_enumeration(self, parent_id: str, name: str, literals: list[str]) -> dict[str, Any]:
        """POST /v1/elements/enumerations — create an enumeration with literals."""
        resp = await self._client.post(
            "/elements/enumerations",
            json={"parentId": parent_id, "name": name, "literals": literals},
        )
        return self._check_and_parse(resp)

    async def add_allocation(self, source_id: str, target_id: str) -> dict[str, Any]:
        """POST /v1/elements/{id}/allocate — allocate source to target."""
        resp = await self._client.post(
            f"/elements/{source_id}/allocate",
            json={"targetId": target_id},
        )
        return self._check_and_parse(resp)

    async def export_diagram_image(self, diagram_id: str) -> dict[str, Any]:
        """GET /v1/diagrams/{id}/export — export diagram as base64 PNG."""
        resp = await self._client.get(f"/diagrams/{diagram_id}/export")
        return self._check_and_parse(resp)

    async def get_ports(self, element_id: str) -> dict[str, Any]:
        """GET /v1/elements/{id}/ports — get all ports with types and connections."""
        resp = await self._client.get(f"/elements/{element_id}/ports")
        return self._check_and_parse(resp)

    # -------------------------------------------------------------------------
    # Safety tier operations
    # -------------------------------------------------------------------------

    async def enable_writes(self, secret: str) -> dict[str, Any]:
        resp = await self._client.post(
            "/safety/enable-writes",
            json={"secret": secret},
        )
        return self._check_and_parse(resp)

    async def enable_dangerous_writes(self, secret: str) -> dict[str, Any]:
        resp = await self._client.post(
            "/safety/enable-dangerous-writes",
            json={"secret": secret},
        )
        return self._check_and_parse(resp)

    async def disable_writes(self) -> dict[str, Any]:
        resp = await self._client.post("/safety/disable-writes")
        return self._check_and_parse(resp)

    async def get_safety_state(self) -> dict[str, Any]:
        resp = await self._client.get("/safety/state")
        return self._check_and_parse(resp)

    async def get_licence(self) -> dict[str, Any]:
        """Return current licence status."""
        resp = await self._client.get("/safety/get-licence")
        return self._check_and_parse(resp)

    # -------------------------------------------------------------------------
    # Internal
    # -------------------------------------------------------------------------

    def _check_and_parse(self, resp: httpx.Response) -> dict[str, Any]:
        if 200 <= resp.status_code < 300:
            return resp.json()
        try:
            problem = resp.json()
        except Exception:
            problem = {
                "type": "https://jgs-sysmlv2-mcp/errors/unknown",
                "title": "Unknown bridge error",
                "status": resp.status_code,
                "detail": resp.text[:500],
            }
        raise problem_to_exception(problem)
