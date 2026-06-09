<!--
  Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
  SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
-->

# JGS SysML v1 MCP Bridge — Tool Reference

_Auto-generated. Do not edit by hand._

**Tier key:**
- **FREE** — read-only; available without write secret
- **PRO** — requires write tier (`enable_writes`)
- **DANGEROUS** — requires dangerous tier (`enable_dangerous_writes`) or dev mode

---

## Lifecycle Tools

Liveness, project persistence, and undo/redo. Source: `lifecycle_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `ping` | Liveness probe — calls the SysML v1 bridge plugin and returns its build metadata. | FREE | — |
| `get_safety_state` | Return the current safety tier (READ, WRITE, or DANGEROUS) plus dev mode status. | FREE | — |
| `get_licence` | Return the current licence status: tier, customer, expiry, validity. | FREE | — |
| `save_project` | Save the current Cameo project. | PRO | `comment: str = ""` |
| `get_edit_history` | Return recent edit history (undo stack) from the open project. | FREE | `max_entries: int = 20` |
| `undo` | Undo the last model edit. | PRO | — |
| `redo` | Redo the last undone model edit. | PRO | — |

---

## Safety Tools

Write-gate and dev-mode controls. Source: `safety_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `enable_writes` | Enable write operations. Requires the write secret. | PRO | `secret: str` |
| `disable_writes` | Disable write operations. Requires the write secret. | PRO | `secret: str` |
| `enable_dangerous_writes` | Enable dangerous write operations (delete, structural changes). Requires the write secret. | DANGEROUS | `secret: str` |
| `enable_dev_mode` | Enable developer mode. Requires the write secret. | PRO | `secret: str` |
| `disable_dev_mode` | Disable developer mode. Requires the write secret. | PRO | `secret: str` |

---

## Batch Tools

Atomic batch session management. Source: `batch_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `begin_batch` | Open a batch session — all writes within are committed atomically on `commit_batch`. | PRO | — |
| `commit_batch` | Commit all queued operations in the given batch session. | PRO | `batch_id: str` |
| `abort_batch` | Roll back all queued operations in the given batch session. | PRO | `batch_id: str` |

---

## Read Tools

Model exploration and lookup. Source: `read_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `get_element` | Retrieve a single SysML v1 element by its local ID. Returns type, name, and owner ID. | FREE | `element_id: str` |
| `find_by_name` | Find all elements whose name contains the given string. Returns list of matches. | FREE | `name: str` |
| `find_by_type` | Find all elements matching a SysML v1 type name (e.g. Block, Requirement, FlowPort). | FREE | `type_name: str` |
| `find_by_qualified_name` | Find an element by its fully-qualified name (e.g. `Model::Package::Block`). | FREE | `qualified_name: str` |
| `get_qualified_name` | Return the fully-qualified name of an element. | FREE | `element_id: str` |
| `get_root_package` | Return the root model package of the open project. | FREE | — |
| `list_children` | List direct children of an element. Returns list with id, name, type. | FREE | `parent_id: str` |
| `walk_tree` | Walk the containment tree from root_id. Returns nested tree structure. | FREE | `root_id: str`, `max_depth: int = 5`, `max_elements: int = 200` |
| `search` | Full-text search across element names. | FREE | `query: str`, `max_results: int = 50` |
| `describe_element` | Return rich description of an element including stereotypes and tagged values. | FREE | `element_id: str` |
| `get_element_structure` | Return the structural hierarchy under an element (parts, ports, properties). | FREE | `element_id: str` |
| `get_relationships` | Return all relationships involving an element. | FREE | `element_id: str` |
| `get_ports` | Return all ports owned by an element. | FREE | `element_id: str` |
| `get_allocations` | List all Allocate relationships from and to an element. | FREE | `element_id: str` |
| `list_applied_stereotypes` | List all stereotypes applied to an element. | FREE | `element_id: str` |
| `find_unit` | Search the model for SysML Unit-stereotyped elements by name substring. | FREE | `name: str` |
| `find_quantity_kind` | Search the model for SysML QuantityKind-stereotyped elements by name substring. | FREE | `name: str` |

---

## Write Tools

Element creation, structural writes, state machine and sequence diagram authoring. Source: `write_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `create_element` | Create a SysML v1 element of the given type under parent_id. Valid types: Block, Package, Requirement, ConstraintBlock, ValueType, InterfaceBlock, FlowPort, ProxyPort, FullPort, PartProperty, ValueProperty, ReferenceProperty, UseCase, Activity, StateMachine, State, Action, Actor, Signal, Class, DataType, Enumeration, Interface. | PRO | `parent_id: str`, `name: str`, `element_type: str` |
| `create_root_model` | Set or rename the root model element. Returns the root model id and name. | PRO | `name: str = "Model"` |
| `create_enumeration` | Create an Enumeration with the given literal names under parent_id. | PRO | `parent_id: str`, `name: str`, `literals: list[str]` |
| `create_connector` | Create a UML Connector between two ConnectableElements (ports, properties). | PRO | `parent_id: str`, `source_id: str`, `target_id: str`, `name: str = ""` |
| `create_item_flow` | Create an ItemFlow on an existing Connector. The item_element_id must be a Classifier. | PRO | `connector_id: str`, `item_element_id: str`, `name: str = ""` |
| `create_binding_connector` | Create a BindingConnector (SysML equal-value constraint) between two properties/ports. | PRO | `parent_id: str`, `source_id: str`, `target_id: str`, `name: str = ""` |
| `create_allocation` | Create an Allocate relationship from source to target (SysML Allocation). | PRO | `source_id: str`, `target_id: str`, `name: str = ""` |
| `create_generalization` | Create a UML Generalization from a specific to a general classifier. | PRO | `specific_id: str`, `general_id: str` |
| `create_diagram` | Create a SysML diagram. kind: BDD, IBD, Parametric, Requirement, Activity, StateMachine, UseCase, Package, Sequence. | PRO | `parent_id: str`, `name: str`, `kind: str` |
| `create_package` | Create a UML Package under parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_transition` | Create a UML Transition between two Vertex elements (States/Pseudostates) in a StateMachine. | PRO | `parent_id: str`, `source_id: str`, `target_id: str` |
| `create_state_machine` | Create a UML StateMachine (with a default Region) owned by parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_state` | Create a State inside a Region. Set is_initial='true' for an initial Pseudostate, is_final='true' for a FinalState. | PRO | `region_id: str`, `name: str`, `is_initial: str = "false"`, `is_final: str = "false"` |
| `create_region` | Create an additional Region inside a StateMachine or composite State. | PRO | `parent_id: str`, `name: str` |
| `set_state_action` | Set an entry, do, or exit action body on a State. action_kind: 'entry', 'do', or 'exit'. | PRO | `state_id: str`, `action_kind: str`, `body: str` |
| `set_transition_trigger` | Add a named Trigger to a Transition. | PRO | `transition_id: str`, `trigger_name: str` |
| `set_transition_guard` | Set an OpaqueExpression guard constraint on a Transition. | PRO | `transition_id: str`, `guard_expression: str` |
| `set_transition_effect` | Set an OpaqueBehavior effect on a Transition. | PRO | `transition_id: str`, `effect_body: str` |
| `create_activity` | Create a UML Activity owned by parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_action` | Create an Action inside an Activity. action_type: OpaqueAction (default), CallBehaviorAction, SendSignalAction. | PRO | `activity_id: str`, `name: str`, `action_type: str = "OpaqueAction"` |
| `create_control_flow` | Create a ControlFlow edge between two ActivityNodes within an Activity. | PRO | `activity_id: str`, `source_id: str`, `target_id: str` |
| `create_object_flow` | Create an ObjectFlow edge between two ActivityNodes within an Activity. | PRO | `activity_id: str`, `source_id: str`, `target_id: str` |
| `create_requirement` | Create a SysML Requirement element under parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_proxy_port` | Create a SysML ProxyPort on a Block. | PRO | `parent_id: str`, `name: str` |
| `create_full_port` | Create a SysML FullPort on a Block. | PRO | `parent_id: str`, `name: str` |
| `create_flow_port` | Create a SysML FlowPort on a Block. | PRO | `parent_id: str`, `name: str` |
| `add_refine` | Create a SysML Refine dependency from source to target. | PRO | `source_id: str`, `target_id: str` |
| `add_copy` | Create a SysML Copy dependency from source to target. | PRO | `source_id: str`, `target_id: str` |
| `add_trace` | Create a UML Trace dependency from source to target (StandardProfile). | PRO | `source_id: str`, `target_id: str` |
| `list_layout_styles` | List available auto-layout styles for a diagram. | FREE | `diagram_id: str` |
| `compare_layout_styles` | Compare how each auto-layout style would affect a diagram. | FREE | `diagram_id: str` |
| `get_edit_history` | Return the edit history (change log) for an element. | FREE | `element_id: str` |
| `create_association` | Create a UML Association between two classifiers. | PRO | `parent_id: str`, `source_id: str`, `target_id: str`, `name: str = ""` |
| `create_association_block` | Create a SysML Association Block (AssociationClass + Block stereotype). | PRO | `parent_id: str`, `source_id: str`, `target_id: str`, `name: str = ""` |
| `create_flow_specification` | Create a SysML FlowSpecification (Interface + FlowSpecification stereotype). | PRO | `parent_id: str`, `name: str` |
| `create_flow_property` | Create a SysML FlowProperty. direction: in \| out \| inout. | PRO | `parent_id: str`, `name: str`, `direction: str` |
| `create_constraint_property` | Create a ConstraintProperty typed by a ConstraintBlock. | PRO | `parent_id: str`, `name: str`, `constraint_block_id: str` |
| `set_encapsulated` | Set the isEncapsulated tagged value on a Block. value: 'true' or 'false'. | PRO | `element_id: str`, `value: str` |
| `set_item_flow_conveyed` | Set the conveyed Classifier on a SysML ItemFlow. | PRO | `item_flow_id: str`, `classifier_id: str` |
| `create_interaction` | Create a UML Interaction (container for sequence diagram content). | PRO | `parent_id: str`, `name: str` |
| `create_lifeline` | Create a Lifeline inside a UML Interaction. | PRO | `interaction_id: str`, `name: str` |
| `create_message` | Create a Message between two Lifelines in an Interaction. Creates send/receive occurrence specs automatically. | PRO | `interaction_id: str`, `name: str`, `sender_lifeline_id: str`, `receiver_lifeline_id: str` |
| `create_combined_fragment` | Create a CombinedFragment in an Interaction. operator: alt \| opt \| loop \| break \| par \| seq \| strict \| neg. | PRO | `interaction_id: str`, `name: str`, `operator: str` |
| `get_standard_library_types` | Return the available standard library DataTypes from the open project. | FREE | — |

---

## Modify Tools

Element rename, delete, move, and property updates. Source: `modify_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `rename_element` | Rename a SysML v1 element. | PRO | `element_id: str`, `new_name: str` |
| `set_documentation` | Set the documentation (owned Comment body) of an element. | PRO | `element_id: str`, `documentation: str` |
| `delete_element` | Permanently delete an element from the model. | DANGEROUS | `element_id: str` |
| `move_element` | Move an element to a new parent (re-owner). | PRO | `element_id: str`, `new_parent_id: str` |
| `set_type` | Set the type of a TypedElement (Property, Parameter, Port, etc.). | PRO | `feature_id: str`, `type_id: str` |
| `set_multiplicity` | Set multiplicity bounds on a MultiplicityElement. Use -1 for upper=*. | PRO | `feature_id: str`, `lower: int`, `upper: int` |
| `set_value` | Set the default value of a Property as a LiteralString. | PRO | `feature_id: str`, `value: str` |
| `set_constraint` | Create a Constraint with an OpaqueExpression body on parent_id. | PRO | `parent_id: str`, `expression: str`, `name: str = ""`, `language: str = ""`, `subject_ids: list[str] \| None = None` |
| `set_property` | Set a tagged value (stereotype property) on an element via TagsHelper. | PRO | `element_id: str`, `property_name: str`, `value: str` |
| `apply_stereotype` | Apply a stereotype to an element by its qualified name. | PRO | `element_id: str`, `stereotype_qn: str` |
| `remove_stereotype` | Remove a stereotype from an element by its qualified name. | PRO | `element_id: str`, `stereotype_qn: str` |
| `set_requirement_id` | Set the SysML requirement ID tagged value on a Requirement element. | PRO | `element_id: str`, `req_id: str` |
| `set_requirement_text` | Set the normative requirement text on a Requirement element. | PRO | `element_id: str`, `text: str` |
| `set_value_type_unit` | Set the unit of a SysML ValueType element. | PRO | `element_id: str`, `unit_id: str` |
| `set_flow_direction` | Set the direction of a Parameter. Valid values: IN, OUT, INOUT, RETURN. | PRO | `element_id: str`, `direction: str` |

---

## Relationship Tools

Requirement traceability and connector end management. Source: `relationship_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `add_satisfy` | Create a Satisfy relationship from a satisfying element to a requirement. | PRO | `satisfying_element_id: str`, `requirement_id: str` |
| `add_verify` | Create a Verify relationship from a verifying element to a requirement. | PRO | `verifying_element_id: str`, `requirement_id: str` |
| `add_derive` | Create a DeriveReqt relationship between two requirements. | PRO | `derived_req_id: str`, `source_req_id: str` |
| `set_connection_ends` | Set source and target ConnectorEnd roles on a Connector. | PRO | `connection_id: str`, `source_end_id: str`, `target_end_id: str` |
| `add_dependency` | Create a UML Dependency between a client and supplier element. | PRO | `client_id: str`, `supplier_id: str`, `name: str = ""` |

---

## Quality Tools

Model analysis, coverage, and traceability reporting. Source: `quality_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `impact_analysis` | Return elements that use or are used by the given element. | FREE | `element_id: str` |
| `validate_model` | Run built-in model validation and return any rule violations. | FREE | — |
| `check_requirement_coverage` | Return coverage statistics: how many requirements are satisfied/verified. | FREE | — |
| `check_documentation_coverage` | Return fraction of named elements that have documentation set. | FREE | — |
| `check_naming_conventions` | Return elements that violate UpperCamelCase / lowerCamelCase conventions. | FREE | — |
| `find_unused_types` | Return classifiers that are not used as a type anywhere in the model. | FREE | — |
| `find_duplicates` | Return elements that share the same type+name combination. | FREE | — |
| `export_requirements_matrix` | Return a full requirements traceability matrix with satisfy/verify links. | FREE | — |
| `trace_requirement` | Return full traceability chain for one requirement (derive, satisfy, verify). | FREE | `requirement_id: str` |
| `generate_model_summary` | Return a high-level summary of model element counts and coverage. | FREE | — |
| `get_model_metrics` | Return raw element counts broken down by UML/SysML type. | FREE | — |

---

## Diagram Tools

Diagram creation, symbol management, layout, and image export. Source: `diagram_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `create_diagram` | Create a SysML v1 diagram. Kinds: BDD, IBD, Parametric, Requirement, Activity, StateMachine, UseCase, Package, Sequence. | PRO | `parent_id: str`, `name: str`, `kind: str` |
| `list_diagrams` | List diagrams owned by a package or element. | FREE | `parent_id: str` |
| `list_diagram_kinds` | Return supported diagram kinds for SysML v1. | FREE | — |
| `add_symbol` | Add an element symbol to a diagram. | PRO | `diagram_id: str`, `element_id: str` |
| `remove_symbol` | Remove an element symbol from a diagram. | PRO | `diagram_id: str`, `element_id: str` |
| `populate_diagram` | Add multiple element symbols to a diagram. | PRO | `diagram_id: str`, `element_ids: list[str]` |
| `auto_layout_diagram` | Apply Cameo's automatic layout to a diagram. | PRO | `diagram_id: str` |
| `list_diagram_symbols` | List all symbols currently in a diagram. | FREE | `diagram_id: str` |
| `export_diagram_image` | Export a diagram as a JPEG image (base64 encoded, max 1024px). Returns MCP ImageContent. | FREE | `diagram_id: str` |
| `list_layout_styles` | Return supported diagram layout styles. | FREE | — |
| `compare_layout_styles` | Compare available layout styles for a diagram. | FREE | `diagram_id: str` |
| `apply_custom_layout` | Apply a named layout style to a diagram. | PRO | `diagram_id: str`, `style: str` |
| `move_symbol` | Move a symbol to specific coordinates. | PRO | `diagram_id: str`, `element_id: str`, `x: int`, `y: int` |
| `resize_symbol` | Resize a symbol in a diagram. | PRO | `diagram_id: str`, `element_id: str`, `width: int`, `height: int` |
| `set_symbol_style` | Set visual style properties on a diagram symbol. | PRO | `diagram_id: str`, `element_id: str`, `style_properties: str` |
| `set_compartment_visibility` | Show or hide a compartment on a symbol. | PRO | `diagram_id: str`, `element_id: str`, `compartment: str`, `visible: bool` |
| `add_path` | Add a relationship path to a diagram. | PRO | `diagram_id: str`, `relationship_id: str` |
| `route_path` | Set routing style for a relationship path. | PRO | `diagram_id: str`, `relationship_id: str`, `routing_style: str` |
| `add_diagram_note` | Add a text note to a diagram. | PRO | `diagram_id: str`, `text: str`, `x: int = 0`, `y: int = 0` |

---

## Macro Tools

Direct JVM script execution. Source: `macro_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `execute_groovy` | Execute Groovy script inside CATIA Magic's JVM with full SysML v1 API access. Requires dev mode active on the plugin side. | DANGEROUS | `script: str` |

---

## V1 Vocabulary Tools

SysML v1 typed convenience wrappers over `create_element`. Source: `v1_tools.py`.

| Tool | Description | Tier | Key Parameters |
|---|---|---|---|
| `create_block` | Create a SysML v1 Block under parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_part_property` | Create a PartProperty (typed composite part) under a Block. | PRO | `parent_id: str`, `name: str` |
| `create_value_property` | Create a ValueProperty (scalar attribute) under a Block. | PRO | `parent_id: str`, `name: str` |
| `create_reference_property` | Create a ReferenceProperty under a Block. | PRO | `parent_id: str`, `name: str` |
| `create_interface_block` | Create a SysML InterfaceBlock under parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_value_type` | Create a SysML ValueType under parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_constraint_block` | Create a SysML ConstraintBlock under parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_use_case` | Create a UseCase element under parent_id. | PRO | `parent_id: str`, `name: str` |
| `create_actor` | Create an Actor element under parent_id. | PRO | `parent_id: str`, `name: str` |

---

> **Note on duplicates:** `list_layout_styles`, `compare_layout_styles`, and `get_edit_history` are registered in both `write_tools.py` and `diagram_tools.py`/`lifecycle_tools.py`. The 136 total above counts raw registrations. Unique tool names: 133.

<!-- total: 136 tools -->
