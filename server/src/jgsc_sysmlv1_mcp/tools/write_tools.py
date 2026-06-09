# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Write/create tools for the SysML v1 MCP bridge."""
from __future__ import annotations
from typing import Any
from magic_mcp_core.domain_server import DomainServer


def register_write_v1_tools(server: DomainServer) -> None:
    """Register v1 create/write tools."""

    @server.mcp.tool()
    async def create_element(parent_id: str, name: str, element_type: str) -> dict[str, Any]:
        """Create a SysML v1 element of the given type under parent_id. Valid types: Block, Package, Requirement, ConstraintBlock, ValueType, InterfaceBlock, FlowPort, ProxyPort, FullPort, PartProperty, ValueProperty, ReferenceProperty, UseCase, Activity, StateMachine, State, Action, Actor, Signal, Class, DataType, Enumeration, Interface."""
        return await server.client.create_element(parent_id, name, element_type)

    @server.mcp.tool()
    async def create_root_model(name: str = "Model") -> dict[str, Any]:
        """Set or rename the root model element. Returns the root model id and name."""
        return await server.client.create_root_model(name=name)

    @server.mcp.tool()
    async def create_enumeration(parent_id: str, name: str, literals: list[str]) -> dict[str, Any]:
        """Create an Enumeration with the given literal names under parent_id."""
        return await server.client.create_enumeration(parent_id, name, literals)

    @server.mcp.tool()
    async def create_connector(parent_id: str, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        """Create a UML Connector between two ConnectableElements (ports, properties)."""
        return await server.client.create_connector(parent_id, source_id, target_id, name=name)

    @server.mcp.tool()
    async def create_item_flow(connector_id: str, item_element_id: str, name: str = "") -> dict[str, Any]:
        """Create an ItemFlow on an existing Connector. The item_element_id must be a Classifier."""
        return await server.client.create_item_flow(connector_id, item_element_id, name=name)

    @server.mcp.tool()
    async def create_binding_connector(parent_id: str, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        """Create a BindingConnector (SysML equal-value constraint) between two properties/ports."""
        return await server.client.create_binding_connector(parent_id, source_id, target_id, name=name)

    @server.mcp.tool()
    async def create_allocation(source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        """Create an Allocate relationship from source to target (SysML Allocation)."""
        return await server.client.create_allocation(source_id, target_id, name=name)

    @server.mcp.tool()
    async def create_generalization(specific_id: str, general_id: str) -> dict[str, Any]:
        """Create a UML Generalization from a specific to a general classifier."""
        return await server.client.create_generalization(specific_id, general_id)

    @server.mcp.tool()
    async def create_diagram(parent_id: str, name: str, kind: str) -> dict[str, Any]:
        """Create a SysML diagram. kind: BDD, IBD, Parametric, Requirement, Activity, StateMachine, UseCase, Package, Sequence."""
        return await server.client.create_diagram(parent_id, name, kind)

    @server.mcp.tool()
    async def create_package(parent_id: str, name: str) -> dict[str, Any]:
        """Create a UML Package under parent_id."""
        return await server.client.create_package(parent_id, name)

    @server.mcp.tool()
    async def create_transition(parent_id: str, source_id: str, target_id: str) -> dict[str, Any]:
        """Create a UML Transition between two Vertex elements (States/Pseudostates) in a StateMachine."""
        return await server.client.create_transition(parent_id, source_id, target_id)

    @server.mcp.tool()
    async def create_state_machine(parent_id: str, name: str) -> dict[str, Any]:
        """Create a UML StateMachine (with a default Region) owned by parent_id."""
        return await server.client.create_state_machine(parent_id, name)

    @server.mcp.tool()
    async def create_state(region_id: str, name: str, is_initial: str = "false", is_final: str = "false") -> dict[str, Any]:
        """Create a State inside a Region. Set is_initial='true' for an initial Pseudostate, is_final='true' for a FinalState."""
        return await server.client.create_state(region_id, name, is_initial=is_initial, is_final=is_final)

    @server.mcp.tool()
    async def create_region(parent_id: str, name: str) -> dict[str, Any]:
        """Create an additional Region inside a StateMachine or composite State (for concurrent/orthogonal regions)."""
        return await server.client.create_region(parent_id, name)

    @server.mcp.tool()
    async def set_state_action(state_id: str, action_kind: str, body: str) -> dict[str, Any]:
        """Set an entry, do, or exit action body on a State. action_kind must be 'entry', 'do', or 'exit'."""
        return await server.client.set_state_action(state_id, action_kind, body)

    @server.mcp.tool()
    async def set_transition_trigger(transition_id: str, trigger_name: str) -> dict[str, Any]:
        """Add a named Trigger to a Transition."""
        return await server.client.set_transition_trigger(transition_id, trigger_name)

    @server.mcp.tool()
    async def set_transition_guard(transition_id: str, guard_expression: str) -> dict[str, Any]:
        """Set an OpaqueExpression guard constraint on a Transition."""
        return await server.client.set_transition_guard(transition_id, guard_expression)

    @server.mcp.tool()
    async def set_transition_effect(transition_id: str, effect_body: str) -> dict[str, Any]:
        """Set an OpaqueBehavior effect on a Transition."""
        return await server.client.set_transition_effect(transition_id, effect_body)

    @server.mcp.tool()
    async def create_activity(parent_id: str, name: str) -> dict[str, Any]:
        """Create a UML Activity owned by parent_id."""
        return await server.client.create_activity(parent_id, name)

    @server.mcp.tool()
    async def create_action(activity_id: str, name: str, action_type: str = "OpaqueAction") -> dict[str, Any]:
        """Create an Action inside an Activity. action_type: OpaqueAction (default), CallBehaviorAction, SendSignalAction."""
        return await server.client.create_action(activity_id, name, action_type=action_type)

    @server.mcp.tool()
    async def create_control_flow(activity_id: str, source_id: str, target_id: str) -> dict[str, Any]:
        """Create a ControlFlow edge between two ActivityNodes within an Activity."""
        return await server.client.create_control_flow(activity_id, source_id, target_id)

    @server.mcp.tool()
    async def create_object_flow(activity_id: str, source_id: str, target_id: str) -> dict[str, Any]:
        """Create an ObjectFlow edge between two ActivityNodes within an Activity."""
        return await server.client.create_object_flow(activity_id, source_id, target_id)

    @server.mcp.tool()
    async def create_requirement(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML Requirement element under parent_id."""
        return await server.client.create_requirement(parent_id, name)

    @server.mcp.tool()
    async def create_proxy_port(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML ProxyPort on a Block."""
        return await server.client.create_proxy_port(parent_id, name)

    @server.mcp.tool()
    async def create_full_port(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML FullPort on a Block."""
        return await server.client.create_full_port(parent_id, name)

    @server.mcp.tool()
    async def create_flow_port(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML FlowPort on a Block."""
        return await server.client.create_flow_port(parent_id, name)


    @server.mcp.tool()
    async def add_refine(source_id: str, target_id: str) -> dict[str, Any]:
        """Create a SysML Refine dependency from source to target."""
        return await server.client.add_refine(source_id, target_id)

    @server.mcp.tool()
    async def add_copy(source_id: str, target_id: str) -> dict[str, Any]:
        """Create a SysML Copy dependency from source to target."""
        return await server.client.add_copy(source_id, target_id)

    @server.mcp.tool()
    async def add_trace(source_id: str, target_id: str) -> dict[str, Any]:
        """Create a UML Trace dependency from source to target (StandardProfile)."""
        return await server.client.add_trace(source_id, target_id)

    @server.mcp.tool()
    async def list_layout_styles(diagram_id: str) -> dict[str, Any]:
        """List available auto-layout styles for a diagram."""
        return await server.client.list_layout_styles(diagram_id)

    @server.mcp.tool()
    async def compare_layout_styles(diagram_id: str) -> dict[str, Any]:
        """Compare how each auto-layout style would affect a diagram."""
        return await server.client.compare_layout_styles(diagram_id)

    @server.mcp.tool()
    async def get_edit_history(element_id: str) -> dict[str, Any]:
        """Return the edit history (change log) for an element."""
        return await server.client.get_edit_history(element_id)

    @server.mcp.tool()
    async def create_association(parent_id: str, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        """Create a UML Association between two classifiers."""
        return await server.client.create_association(parent_id, source_id, target_id, name=name)

    @server.mcp.tool()
    async def create_association_block(parent_id: str, source_id: str, target_id: str, name: str = "") -> dict[str, Any]:
        """Create a SysML Association Block (AssociationClass + Block stereotype)."""
        return await server.client.create_association_block(parent_id, source_id, target_id, name=name)

    @server.mcp.tool()
    async def create_flow_specification(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML FlowSpecification (Interface + FlowSpecification stereotype)."""
        return await server.client.create_flow_specification(parent_id, name)

    @server.mcp.tool()
    async def create_flow_property(parent_id: str, name: str, direction: str) -> dict[str, Any]:
        """Create a SysML FlowProperty. direction: in | out | inout."""
        return await server.client.create_flow_property(parent_id, name, direction)

    @server.mcp.tool()
    async def create_constraint_property(parent_id: str, name: str, constraint_block_id: str) -> dict[str, Any]:
        """Create a ConstraintProperty typed by a ConstraintBlock."""
        return await server.client.create_constraint_property(parent_id, name, constraint_block_id)

    @server.mcp.tool()
    async def set_encapsulated(element_id: str, value: str) -> dict[str, Any]:
        """Set the isEncapsulated tagged value on a Block. value: 'true' or 'false'."""
        return await server.client.set_encapsulated(element_id, value)

    @server.mcp.tool()
    async def set_item_flow_conveyed(item_flow_id: str, classifier_id: str) -> dict[str, Any]:
        """Set the conveyed Classifier on a SysML ItemFlow."""
        return await server.client.set_item_flow_conveyed(item_flow_id, classifier_id)

    @server.mcp.tool()
    async def create_interaction(parent_id: str, name: str) -> dict[str, Any]:
        """Create a UML Interaction (container for sequence diagram content)."""
        return await server.client.create_interaction(parent_id, name)

    @server.mcp.tool()
    async def create_lifeline(interaction_id: str, name: str) -> dict[str, Any]:
        """Create a Lifeline inside a UML Interaction."""
        return await server.client.create_lifeline(interaction_id, name)

    @server.mcp.tool()
    async def create_message(interaction_id: str, name: str, sender_lifeline_id: str, receiver_lifeline_id: str) -> dict[str, Any]:
        """Create a Message between two Lifelines in an Interaction. Creates send/receive occurrence specs automatically."""
        return await server.client.create_message(interaction_id, name, sender_lifeline_id, receiver_lifeline_id)

    @server.mcp.tool()
    async def create_combined_fragment(interaction_id: str, name: str, operator: str) -> dict[str, Any]:
        """Create a CombinedFragment in an Interaction. operator: alt | opt | loop | break | par | seq | strict | neg."""
        return await server.client.create_combined_fragment(interaction_id, name, operator)

    @server.mcp.tool()
    async def get_standard_library_types() -> dict[str, Any]:
        """Return the available standard library DataTypes from the open project."""
        return await server.client.get_standard_library_types()
