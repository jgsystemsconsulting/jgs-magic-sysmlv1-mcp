# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
#
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary

"""Thin async HTTP client for the v1 bridge plugin — endpoint + token from env."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Generator

import httpx

from magic_mcp_core.errors import BridgeError, problem_to_exception


class _TokenFileAuth(httpx.Auth):
    """Reads the bearer token from a file on every request.

    Falls back to a static token string when no file path is given or the file
    cannot be read. This avoids the need to restart the MCP process after each
    MSOSA restart (which rotates the token file).
    """

    def __init__(self, token_file: Path | None, static_token: str | None) -> None:
        self._token_file = token_file
        self._static_token = static_token

    def _current_token(self) -> str | None:
        if self._token_file is not None:
            try:
                tok = self._token_file.read_text(encoding="utf-8").strip()
                if tok:
                    return tok
            except OSError:
                pass
        return self._static_token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        token = self._current_token()
        if token:
            request.headers["Authorization"] = f"Bearer {token}"
        yield request


class HttpClient:
    """Async HTTP client for the v1 bridge plugin.

    Pass ``token_file`` to re-read the bearer token on every request (survives
    MSOSA restarts without restarting the MCP process). ``static_token`` is used
    as a fallback when the file is absent or unreadable.
    """

    def __init__(
        self,
        endpoint: str,
        token: str | None = None,
        *,
        token_file: Path | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        auth = _TokenFileAuth(token_file=token_file, static_token=token)
        self._client = httpx.AsyncClient(
            base_url=self._endpoint + "/v1",
            auth=auth,
            timeout=timeout_seconds,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    # -----------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------

    async def ping(self) -> dict[str, Any]:
        try:
            resp = await self._client.get("/ping")
        except httpx.ConnectError as ce:
            raise BridgeError({
                "type": "https://jgs-sysmlv1-mcp/errors/plugin-not-running",
                "title": "Plugin not running",
                "status": 503,
                "detail": f"could not connect to v1 bridge at {self._endpoint}: {ce}",
            }) from ce
        return self._check_and_parse(resp)

    async def get_plugin_info(self) -> dict[str, Any]:
        resp = await self._client.get("/plugin/info")
        return self._check_and_parse(resp)

    # -----------------------------------------------------------------
    # Read operations
    # -----------------------------------------------------------------

    async def get_element(self, element_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"/elements/{element_id}")
        return self._check_and_parse(resp)

    # -----------------------------------------------------------------
    async def create_requirement(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template('create_element', parent_id=parent_id, name=name, element_type='Requirement')

    async def create_proxy_port(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template('create_element', parent_id=parent_id, name=name, element_type='ProxyPort')

    async def create_full_port(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template('create_element', parent_id=parent_id, name=name, element_type='FullPort')

    async def create_flow_port(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template('create_element', parent_id=parent_id, name=name, element_type='FlowPort')


    # Sprint 1 additions (gap closure 2026-05-31)
    # -----------------------------------------------------------------

    async def add_refine(self, source_id: str, target_id: str) -> dict[str, Any]:
        # Bridge template add_refine expects params {refining_element_id, requirement_id}.
        return await self._run_template(
            'add_refine', refining_element_id=source_id, requirement_id=target_id)

    async def add_copy(self, source_id: str, target_id: str) -> dict[str, Any]:
        # Bridge template add_copy expects params {copy_element_id, source_req_id}.
        return await self._run_template(
            'add_copy', copy_element_id=source_id, source_req_id=target_id)

    async def add_trace(self, source_id: str, target_id: str) -> dict[str, Any]:
        # Bridge template add_trace expects params {client_id, supplier_id}.
        return await self._run_template(
            'add_trace', client_id=source_id, supplier_id=target_id)

    async def list_layout_styles(self, diagram_id: str) -> dict[str, Any]:
        return await self._run_template('list_layout_styles', diagram_id=diagram_id)

    async def compare_layout_styles(self, diagram_id: str) -> dict[str, Any]:
        return await self._run_template('compare_layout_styles', diagram_id=diagram_id)

    async def get_edit_history(self, element_id: str) -> dict[str, Any]:
        return await self._run_template('get_edit_history', element_id=element_id)

    # -----------------------------------------------------------------
    # Sprint 3 additions
    # -----------------------------------------------------------------

    async def create_association(self, parent_id: str, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        return await self._run_template('create_association', parent_id=parent_id, source_id=source_id, target_id=target_id, name=name)

    async def create_association_block(self, parent_id: str, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        return await self._run_template('create_association_block', parent_id=parent_id, source_id=source_id, target_id=target_id, name=name)

    async def create_flow_specification(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template('create_flow_specification', parent_id=parent_id, name=name)

    async def create_flow_property(self, parent_id: str, name: str, direction: str) -> dict[str, Any]:
        return await self._run_template('create_flow_property', parent_id=parent_id, name=name, direction=direction)

    async def create_constraint_property(self, parent_id: str, name: str, constraint_block_id: str) -> dict[str, Any]:
        return await self._run_template('create_constraint_property', parent_id=parent_id, name=name, constraint_block_id=constraint_block_id)

    async def set_encapsulated(self, element_id: str, value: str) -> dict[str, Any]:
        return await self._run_template('set_encapsulated', element_id=element_id, value=value)

    async def get_allocations(self, element_id: str) -> dict[str, Any]:
        return await self._run_template('get_allocations', element_id=element_id)

    async def list_applied_stereotypes(self, element_id: str) -> dict[str, Any]:
        return await self._run_template('list_applied_stereotypes', element_id=element_id)

    async def find_unit(self, name: str) -> dict[str, Any]:
        return await self._run_template('find_unit', name=name)

    async def find_quantity_kind(self, name: str) -> dict[str, Any]:
        return await self._run_template('find_quantity_kind', name=name)

    async def set_item_flow_conveyed(self, item_flow_id: str, classifier_id: str) -> dict[str, Any]:
        return await self._run_template('set_item_flow_conveyed', item_flow_id=item_flow_id, classifier_id=classifier_id)

    # -----------------------------------------------------------------
    # Spike 4: Sequence diagram additions
    # -----------------------------------------------------------------

    async def create_interaction(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template('create_interaction', parent_id=parent_id, name=name)

    async def create_lifeline(self, interaction_id: str, name: str) -> dict[str, Any]:
        return await self._run_template('create_lifeline', interaction_id=interaction_id, name=name)

    async def create_message(self, interaction_id: str, name: str, sender_lifeline_id: str, receiver_lifeline_id: str) -> dict[str, Any]:
        return await self._run_template('create_message', interaction_id=interaction_id, name=name, sender_lifeline_id=sender_lifeline_id, receiver_lifeline_id=receiver_lifeline_id)

    async def create_combined_fragment(self, interaction_id: str, name: str, operator: str) -> dict[str, Any]:
        return await self._run_template('create_combined_fragment', interaction_id=interaction_id, name=name, operator=operator)


    # -----------------------------------------------------------------
    # Safety tier
    # -----------------------------------------------------------------

    async def get_safety_state(self) -> dict[str, Any]:
        resp = await self._client.get("/safety/state")
        return self._check_and_parse(resp)

    async def get_licence(self) -> dict[str, Any]:
        resp = await self._client.get("/safety/get-licence")
        return self._check_and_parse(resp)

    # -----------------------------------------------------------------
    # Template dispatcher
    # -----------------------------------------------------------------

    async def _run_template(self, template_name: str, **params) -> dict[str, Any]:
        """POST to /macros/execute-template and unwrap the result string as JSON.

        Java handleExecuteTemplate wraps results as:
            Success: {"success": true, "result": "<JSON string>", "output": "<groovy stdout>"}
            Failure: {"success": false, "output": "<groovy stdout + exception message>"}
        """
        body = {"template": template_name, "params": params}
        resp = await self._client.post("/macros/execute-template", json=body)
        wrapper = self._check_and_parse(resp)  # raises on HTTP error
        if wrapper.get("success") is False:
            raise RuntimeError(
                f"Template '{template_name}' failed on Java side: {wrapper.get('output', '(no output)')}"
            )
        import json as _json
        raw = wrapper.get("result", "{}")
        try:
            return _json.loads(raw) if isinstance(raw, str) else raw
        except _json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Template '{template_name}' returned non-JSON result: {raw[:200]!r}"
            ) from exc

    # -----------------------------------------------------------------
    # Read template methods
    # -----------------------------------------------------------------

    async def find_by_name(self, name: str, max_results: int = 50) -> dict[str, Any]:
        return await self._run_template("find_by_name", name=name, max_results=max_results)

    async def find_by_type(self, type_name: str, max_results: int = 50) -> dict[str, Any]:
        return await self._run_template("find_by_type", type_name=type_name, max_results=max_results)

    async def find_by_qualified_name(self, qualified_name: str) -> dict[str, Any]:
        return await self._run_template("find_by_qualified_name", qualified_name=qualified_name)

    async def list_children(self, parent_id: str) -> dict[str, Any]:
        return await self._run_template("list_children", parent_id=parent_id)

    async def walk_tree(self, root_id: str, max_depth: int = 5, max_elements: int = 200) -> dict[str, Any]:
        return await self._run_template("walk_tree", root_id=root_id, max_depth=max_depth, max_elements=max_elements)

    async def search(self, query: str, max_results: int = 50) -> dict[str, Any]:
        return await self._run_template("search", query=query, max_results=max_results)

    async def describe_element(self, element_id: str) -> dict[str, Any]:
        return await self._run_template("describe_element", element_id=element_id)

    async def get_element_structure(self, element_id: str) -> dict[str, Any]:
        return await self._run_template("get_element_structure", element_id=element_id)

    async def get_relationships(self, element_id: str) -> dict[str, Any]:
        return await self._run_template("get_relationships", element_id=element_id)

    async def get_ports(self, element_id: str) -> dict[str, Any]:
        return await self._run_template("get_ports", element_id=element_id)

    async def get_qualified_name(self, element_id: str) -> dict[str, Any]:
        return await self._run_template("get_qualified_name", element_id=element_id)

    async def get_root_package(self) -> dict[str, Any]:
        return await self._run_template("get_root_package")

    # -----------------------------------------------------------------
    # Lifecycle operations
    # -----------------------------------------------------------------

    async def save_project(self, comment: str = "") -> dict[str, Any]:
        return await self._run_template("save_project", comment=comment)

    async def get_edit_history(self, max_entries: int = 20) -> dict[str, Any]:
        return await self._run_template("get_edit_history", max_entries=max_entries)

    async def undo(self) -> dict[str, Any]:
        return await self._run_template("undo")

    async def redo(self) -> dict[str, Any]:
        return await self._run_template("redo")

    # -----------------------------------------------------------------
    # Write/create operations — all Groovy-backed via _run_template
    # -----------------------------------------------------------------

    async def create_element(self, parent_id: str, name: str, element_type: str) -> dict[str, Any]:
        return await self._run_template("create_element", parent_id=parent_id, name=name, element_type=element_type)

    async def create_root_model(self, name: str = "Model") -> dict[str, Any]:
        return await self._run_template("create_root_model", name=name)

    async def create_enumeration(self, parent_id: str, name: str, literals: list[str]) -> dict[str, Any]:
        # Engine ParamSpec only allows scalar types; pass list as comma-joined string.
        # Groovy template splits on ',' and trims.
        literals_str = ",".join(literals)
        return await self._run_template("create_enumeration", parent_id=parent_id, name=name, literals=literals_str)

    async def create_connector(self, parent_id: str, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        return await self._run_template("create_connector", parent_id=parent_id, source_id=source_id, target_id=target_id, name=name)

    async def create_item_flow(self, connector_id: str, item_element_id: str, name: str = "") -> dict[str, Any]:
        return await self._run_template("create_item_flow", connector_id=connector_id, item_element_id=item_element_id, name=name)

    async def create_binding_connector(self, parent_id: str, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        return await self._run_template("create_binding_connector", parent_id=parent_id, source_id=source_id, target_id=target_id, name=name)

    async def create_allocation(self, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        return await self._run_template("create_allocation", source_id=source_id, target_id=target_id, name=name)

    async def create_generalization(self, specific_id: str, general_id: str) -> dict[str, Any]:
        return await self._run_template("create_generalization", specific_id=specific_id, general_id=general_id)

    async def create_diagram(self, parent_id: str, name: str, kind: str) -> dict[str, Any]:
        return await self._run_template("create_diagram", parent_id=parent_id, name=name, kind=kind)

    async def create_package(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template("create_package", parent_id=parent_id, name=name)

    async def create_transition(self, parent_id: str, source_id: str, target_id: str) -> dict[str, Any]:
        return await self._run_template("create_transition", parent_id=parent_id, source_id=source_id, target_id=target_id)
    async def create_state_machine(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template("create_state_machine", parent_id=parent_id, name=name)

    async def create_state(self, region_id: str, name: str, is_initial: str = "false", is_final: str = "false") -> dict[str, Any]:
        return await self._run_template("create_state", region_id=region_id, name=name, is_initial=is_initial, is_final=is_final)

    async def create_region(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template("create_region", parent_id=parent_id, name=name)

    async def set_state_action(self, state_id: str, action_kind: str, body: str) -> dict[str, Any]:
        return await self._run_template("set_state_action", state_id=state_id, action_kind=action_kind, body=body)

    async def set_transition_trigger(self, transition_id: str, trigger_name: str) -> dict[str, Any]:
        return await self._run_template("set_transition_trigger", transition_id=transition_id, trigger_name=trigger_name)

    async def set_transition_guard(self, transition_id: str, guard_expression: str) -> dict[str, Any]:
        return await self._run_template("set_transition_guard", transition_id=transition_id, guard_expression=guard_expression)

    async def set_transition_effect(self, transition_id: str, effect_body: str) -> dict[str, Any]:
        return await self._run_template("set_transition_effect", transition_id=transition_id, effect_body=effect_body)

    async def create_activity(self, parent_id: str, name: str) -> dict[str, Any]:
        return await self._run_template("create_activity", parent_id=parent_id, name=name)

    async def create_action(self, activity_id: str, name: str, action_type: str = "OpaqueAction") -> dict[str, Any]:
        return await self._run_template("create_action", activity_id=activity_id, name=name, action_type=action_type)

    async def create_control_flow(self, activity_id: str, source_id: str, target_id: str) -> dict[str, Any]:
        return await self._run_template("create_control_flow", activity_id=activity_id, source_id=source_id, target_id=target_id)

    async def create_object_flow(self, activity_id: str, source_id: str, target_id: str) -> dict[str, Any]:
        return await self._run_template("create_object_flow", activity_id=activity_id, source_id=source_id, target_id=target_id)

    async def get_standard_library_types(self) -> dict[str, Any]:
        return await self._run_template("get_standard_library_types")

    # -----------------------------------------------------------------
    # Modify operations — all Groovy-backed via _run_template
    # -----------------------------------------------------------------

    async def rename_element(self, element_id: str, new_name: str) -> dict[str, Any]:
        return await self._run_template("rename_element", element_id=element_id, new_name=new_name)

    async def set_documentation(self, element_id: str, documentation: str) -> dict[str, Any]:
        return await self._run_template("set_documentation", element_id=element_id, documentation=documentation)

    async def set_type(self, feature_id: str, type_id: str) -> dict[str, Any]:
        return await self._run_template("set_type", feature_id=feature_id, type_id=type_id)

    async def set_multiplicity(self, feature_id: str, lower: int, upper: int) -> dict[str, Any]:
        return await self._run_template("set_multiplicity", feature_id=feature_id, lower=lower, upper=upper)

    async def set_value(self, feature_id: str, value: object) -> dict[str, Any]:
        return await self._run_template("set_value", feature_id=feature_id, value=value)

    async def delete_element(self, element_id: str) -> dict[str, Any]:
        return await self._run_template("delete_element", element_id=element_id)

    async def move_element(self, element_id: str, new_parent_id: str) -> dict[str, Any]:
        return await self._run_template("move_element", element_id=element_id, new_parent_id=new_parent_id)

    async def set_constraint(self, parent_id: str, expression: str, name: str = "", language: str = "", subject_ids: list[str] | None = None) -> dict[str, Any]:
        return await self._run_template("set_constraint", parent_id=parent_id, expression=expression, name=name, language=language, subject_ids=subject_ids or [])

    async def set_property(self, element_id: str, property_name: str, value: object) -> dict[str, Any]:
        return await self._run_template("set_property", element_id=element_id, property_name=property_name, value=value)

    async def apply_stereotype(self, element_id: str, stereotype_qn: str) -> dict[str, Any]:
        return await self._run_template("apply_stereotype", element_id=element_id, stereotype_qn=stereotype_qn)

    async def remove_stereotype(self, element_id: str, stereotype_qn: str) -> dict[str, Any]:
        return await self._run_template("remove_stereotype", element_id=element_id, stereotype_qn=stereotype_qn)

    async def set_requirement_id(self, element_id: str, req_id: str) -> dict[str, Any]:
        return await self._run_template("set_requirement_id", element_id=element_id, req_id=req_id)

    async def set_requirement_text(self, element_id: str, text: str) -> dict[str, Any]:
        return await self._run_template("set_requirement_text", element_id=element_id, req_text=text)

    async def set_value_type_unit(self, element_id: str, unit_id: str) -> dict[str, Any]:
        return await self._run_template("set_value_type_unit", element_id=element_id, unit_id=unit_id)

    async def set_flow_direction(self, element_id: str, direction: str) -> dict[str, Any]:
        return await self._run_template("set_flow_direction", element_id=element_id, direction=direction)

    # -----------------------------------------------------------------
    # Relationship operations — all Groovy-backed via _run_template
    # -----------------------------------------------------------------

    async def add_satisfy(self, satisfying_element_id: str, requirement_id: str) -> dict[str, Any]:
        return await self._run_template("add_satisfy", satisfying_element_id=satisfying_element_id, requirement_id=requirement_id)

    async def add_verify(self, verifying_element_id: str, requirement_id: str) -> dict[str, Any]:
        return await self._run_template("add_verify", verifying_element_id=verifying_element_id, requirement_id=requirement_id)

    async def add_derive(self, derived_req_id: str, source_req_id: str) -> dict[str, Any]:
        return await self._run_template("add_derive", derived_req_id=derived_req_id, source_req_id=source_req_id)

    async def set_connection_ends(self, connection_id: str, source_end_id: str, target_end_id: str) -> dict[str, Any]:
        return await self._run_template("set_connection_ends", connection_id=connection_id, source_end_id=source_end_id, target_end_id=target_end_id)

    async def add_dependency(self, client_id: str, supplier_id: str, name: str = "") -> dict[str, Any]:
        return await self._run_template("add_dependency", client_id=client_id, supplier_id=supplier_id, name=name)

    # -----------------------------------------------------------------
    # Diagram operations — all Groovy-backed via _run_template
    # -----------------------------------------------------------------

    async def list_diagrams(self, parent_id: str) -> dict[str, Any]:
        return await self._run_template("list_diagrams", parent_id=parent_id)

    async def list_diagram_kinds(self) -> dict[str, Any]:
        return await self._run_template("list_diagram_kinds")

    async def add_symbol(self, diagram_id: str, element_id: str) -> dict[str, Any]:
        return await self._run_template("add_symbol", diagram_id=diagram_id, element_id=element_id)

    async def remove_symbol(self, diagram_id: str, element_id: str) -> dict[str, Any]:
        return await self._run_template("remove_symbol", diagram_id=diagram_id, element_id=element_id)

    async def populate_diagram(self, diagram_id: str, element_ids: list[str]) -> dict[str, Any]:
        return await self._run_template("populate_diagram", diagram_id=diagram_id, element_ids=",".join(element_ids))

    async def auto_layout_diagram(self, diagram_id: str) -> dict[str, Any]:
        return await self._run_template("auto_layout_diagram", diagram_id=diagram_id)

    async def list_diagram_symbols(self, diagram_id: str) -> dict[str, Any]:
        return await self._run_template("list_diagram_symbols", diagram_id=diagram_id)

    async def export_diagram_image(self, diagram_id: str) -> dict[str, Any]:
        return await self._run_template("export_diagram_image", diagram_id=diagram_id)

    async def list_layout_styles(self) -> dict[str, Any]:
        return await self._run_template("list_layout_styles")

    async def compare_layout_styles(self, diagram_id: str) -> dict[str, Any]:
        return await self._run_template("compare_layout_styles", diagram_id=diagram_id)

    async def apply_custom_layout(self, diagram_id: str, style: str) -> dict[str, Any]:
        return await self._run_template("apply_custom_layout", diagram_id=diagram_id, style=style)

    async def move_symbol(self, diagram_id: str, element_id: str, x: int, y: int) -> dict[str, Any]:
        return await self._run_template("move_symbol", diagram_id=diagram_id, element_id=element_id, x=x, y=y)

    async def resize_symbol(self, diagram_id: str, element_id: str, width: int, height: int) -> dict[str, Any]:
        return await self._run_template("resize_symbol", diagram_id=diagram_id, element_id=element_id, width=width, height=height)

    async def set_symbol_style(self, diagram_id: str, element_id: str, style_properties: str) -> dict[str, Any]:
        return await self._run_template("set_symbol_style", diagram_id=diagram_id, element_id=element_id, style_properties=style_properties)

    async def set_compartment_visibility(self, diagram_id: str, element_id: str, compartment: str, visible: bool) -> dict[str, Any]:
        return await self._run_template("set_compartment_visibility", diagram_id=diagram_id, element_id=element_id, compartment=compartment, visible=visible)

    async def add_path(self, diagram_id: str, relationship_id: str) -> dict[str, Any]:
        return await self._run_template("add_path", diagram_id=diagram_id, relationship_id=relationship_id)

    async def route_path(self, diagram_id: str, relationship_id: str, routing_style: str) -> dict[str, Any]:
        return await self._run_template("route_path", diagram_id=diagram_id, relationship_id=relationship_id, routing_style=routing_style)

    async def add_diagram_note(self, diagram_id: str, text: str, x: int = 0, y: int = 0) -> dict[str, Any]:
        return await self._run_template("add_diagram_note", diagram_id=diagram_id, text=text, x=x, y=y)

    # -----------------------------------------------------------------
    # Quality / traceability — all Groovy-backed via _run_template
    # -----------------------------------------------------------------

    async def impact_analysis(self, element_id: str) -> dict[str, Any]:
        return await self._run_template("impact_analysis", element_id=element_id)

    async def validate_model(self) -> dict[str, Any]:
        return await self._run_template("validate_model")

    async def check_requirement_coverage(self) -> dict[str, Any]:
        return await self._run_template("check_requirement_coverage")

    async def check_documentation_coverage(self) -> dict[str, Any]:
        return await self._run_template("check_documentation_coverage")

    async def check_naming_conventions(self) -> dict[str, Any]:
        return await self._run_template("check_naming_conventions")

    async def find_unused_types(self) -> dict[str, Any]:
        return await self._run_template("find_unused_types")

    async def find_duplicates(self) -> dict[str, Any]:
        return await self._run_template("find_duplicates")

    async def export_requirements_matrix(self) -> dict[str, Any]:
        return await self._run_template("export_requirements_matrix")

    async def trace_requirement(self, requirement_id: str) -> dict[str, Any]:
        return await self._run_template("trace_requirement", requirement_id=requirement_id)

    async def generate_model_summary(self) -> dict[str, Any]:
        return await self._run_template("generate_model_summary")

    async def get_model_metrics(self) -> dict[str, Any]:
        return await self._run_template("get_model_metrics")

    # -----------------------------------------------------------------
    # Safety / write-gate — Java routes (not Groovy templates)
    # -----------------------------------------------------------------

    async def enable_writes(self, secret: str) -> dict[str, Any]:
        resp = await self._client.post("/safety/enable-writes", json={"secret": secret})
        return self._check_and_parse(resp)

    async def disable_writes(self, secret: str) -> dict[str, Any]:
        resp = await self._client.post("/safety/disable-writes", json={"secret": secret})
        return self._check_and_parse(resp)

    async def enable_dangerous_writes(self, secret: str) -> dict[str, Any]:
        resp = await self._client.post("/safety/enable-dangerous-writes", json={"secret": secret})
        return self._check_and_parse(resp)

    async def enable_dev_mode(self, secret: str) -> dict[str, Any]:
        resp = await self._client.post("/safety/enable-dev-mode", json={"secret": secret})
        return self._check_and_parse(resp)

    async def disable_dev_mode(self, secret: str) -> dict[str, Any]:
        resp = await self._client.post("/safety/disable-dev-mode", json={"secret": secret})
        return self._check_and_parse(resp)

    # -----------------------------------------------------------------
    # Batch operations — Java routes (not Groovy templates)
    # -----------------------------------------------------------------

    async def begin_batch(self) -> dict[str, Any]:
        resp = await self._client.post("/batch/begin", json={"name": "batch"})
        return self._check_and_parse(resp)

    async def commit_batch(self, batch_id: str) -> dict[str, Any]:
        resp = await self._client.post(f"/batch/{batch_id}/commit", json={})
        return self._check_and_parse(resp)

    async def abort_batch(self, batch_id: str) -> dict[str, Any]:
        resp = await self._client.post(f"/batch/{batch_id}/abort", json={})
        return self._check_and_parse(resp)

    async def execute_groovy(self, script: str) -> dict[str, Any]:
        """Execute a raw Groovy script inside CATIA Magic's JVM.

        POSTs to /macros/execute (resolves to <endpoint>/v1/macros/execute because
        self._client.base_url is constructed as <endpoint>/v1; do NOT include the
        /v1 prefix in the path argument).

        The bridge requires:
          - dev_mode active on the session (call enable_dev_mode first)
          - an open v1 project in CATIA Magic

        Returns the bridge's JSON response containing keys (matching v2's shape):
          success: true | false
          result:  script return value via String.valueOf (only on success; "null" if script returned null)
          output:  captured stdout/stderr from the script
          error:   exception message (only when success == false)

        Raises BridgeError on HTTP-level failure (non-2xx response). Uses the
        established _check_and_parse() idiom that every other v1 client method uses.
        """
        resp = await self._client.post("/macros/execute", json={"script": script})
        return self._check_and_parse(resp)

    # -----------------------------------------------------------------
    # Internal
    # -----------------------------------------------------------------

    def _check_and_parse(self, resp: httpx.Response) -> dict[str, Any]:
        if 200 <= resp.status_code < 300:
            return resp.json()
        try:
            problem = resp.json()
        except Exception:
            problem = {
                "type": "https://jgs-sysmlv1-mcp/errors/unknown",
                "title": "Unknown bridge error",
                "status": resp.status_code,
                "detail": resp.text[:500],
            }
        raise problem_to_exception(problem)
