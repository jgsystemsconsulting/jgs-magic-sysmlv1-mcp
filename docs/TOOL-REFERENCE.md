<!--
  Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
  SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
-->

# JGS SysML v1 MCP Bridge — Tool Reference


**Tier key:**
- **FREE** — read-only; available without write secret
- **PRO** — requires write tier (`enable_writes`)
- **DANGEROUS** — requires dangerous tier (`enable_dangerous_writes`) or dev mode

---

## Lifecycle Tools

Liveness, project persistence, and undo/redo. Source: `lifecycle_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `ping` | Liveness probe — calls the SysML v1 bridge plugin and returns its build metadata. | FREE |
| `get_safety_state` | Return the current safety tier (READ, WRITE, or DANGEROUS) plus dev mode status. | FREE |
| `get_licence` | Return the current licence status: tier, customer, expiry, validity. | FREE |
| `save_project` | Save the current Cameo project. | PRO |
| `get_edit_history` | Return recent edit history (undo stack) from the open project. | FREE |
| `undo` | Undo the last model edit. | PRO |
| `redo` | Redo the last undone model edit. | PRO |

---

## Safety Tools

Write-gate and dev-mode controls. Source: `safety_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `enable_writes` | Enable write operations. Requires the write secret. | PRO |
| `disable_writes` | Disable write operations. Requires the write secret. | PRO |
| `enable_dangerous_writes` | Enable dangerous write operations (delete, structural changes). Requires the write secret. | DANGEROUS |
| `enable_dev_mode` | Enable developer mode. Requires the write secret. | PRO |
| `disable_dev_mode` | Disable developer mode. Requires the write secret. | PRO |

---

## Batch Tools

Atomic batch session management. Source: `batch_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `begin_batch` | Open a batch session — all writes within are committed atomically on `commit_batch`. | PRO |
| `commit_batch` | Commit all queued operations in the given batch session. | PRO |
| `abort_batch` | Roll back all queued operations in the given batch session. | PRO |

---

## Read Tools

Model exploration and lookup. Source: `read_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `get_element` | Retrieve a single SysML v1 element by its local ID. Returns type, name, and owner ID. | FREE |
| `find_by_name` | Find all elements whose name contains the given string. Returns list of matches. | FREE |
| `find_by_type` | Find all elements matching a SysML v1 type name (e.g. Block, Requirement, FlowPort). | FREE |
| `find_by_qualified_name` | Find an element by its fully-qualified name (e.g. `Model::Package::Block`). | FREE |
| `get_qualified_name` | Return the fully-qualified name of an element. | FREE |
| `get_root_package` | Return the root model package of the open project. | FREE |
| `list_children` | List direct children of an element. Returns list with id, name, type. | FREE |
| `walk_tree` | Walk the containment tree from root_id. Returns nested tree structure. | FREE |
| `search` | Full-text search across element names. | FREE |
| `describe_element` | Return rich description of an element including stereotypes and tagged values. | FREE |
| `get_element_structure` | Return the structural hierarchy under an element (parts, ports, properties). | FREE |
| `get_relationships` | Return all relationships involving an element. | FREE |
| `get_ports` | Return all ports owned by an element. | FREE |
| `get_allocations` | List all Allocate relationships from and to an element. | FREE |
| `list_applied_stereotypes` | List all stereotypes applied to an element. | FREE |
| `find_unit` | Search the model for SysML Unit-stereotyped elements by name substring. | FREE |
| `find_quantity_kind` | Search the model for SysML QuantityKind-stereotyped elements by name substring. | FREE |

---

## Write Tools

Element creation, structural writes, state machine and sequence diagram authoring. Source: `write_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `create_element` | Create a SysML v1 element of the given type under parent_id. Valid types: Block, Package, Requirement, ConstraintBlock, ValueType, InterfaceBlock, FlowPort, ProxyPort, FullPort, PartProperty, ValueProperty, ReferenceProperty, UseCase, Activity, StateMachine, State, Action, Actor, Signal, Class, DataType, Enumeration, Interface. | PRO |
| `create_root_model` | Set or rename the root model element. Returns the root model id and name. | PRO |
| `create_enumeration` | Create an Enumeration with the given literal names under parent_id. | PRO |
| `create_connector` | Create a UML Connector between two ConnectableElements (ports, properties). | PRO |
| `create_item_flow` | Create an ItemFlow on an existing Connector. The item_element_id must be a Classifier. | PRO |
| `create_binding_connector` | Create a BindingConnector (SysML equal-value constraint) between two properties/ports. | PRO |
| `create_allocation` | Create an Allocate relationship from source to target (SysML Allocation). | PRO |
| `create_generalization` | Create a UML Generalization from a specific to a general classifier. | PRO |
| `create_diagram` | Create a SysML diagram. kind: BDD, IBD, Parametric, Requirement, Activity, StateMachine, UseCase, Package, Sequence. | PRO |
| `create_package` | Create a UML Package under parent_id. | PRO |
| `create_transition` | Create a UML Transition between two Vertex elements (States/Pseudostates) in a StateMachine. | PRO |
| `create_state_machine` | Create a UML StateMachine (with a default Region) owned by parent_id. | PRO |
| `create_state` | Create a State inside a Region. Set is_initial='true' for an initial Pseudostate, is_final='true' for a FinalState. | PRO |
| `create_region` | Create an additional Region inside a StateMachine or composite State. | PRO |
| `set_state_action` | Set an entry, do, or exit action body on a State. action_kind: 'entry', 'do', or 'exit'. | PRO |
| `set_transition_trigger` | Add a named Trigger to a Transition. | PRO |
| `set_transition_guard` | Set an OpaqueExpression guard constraint on a Transition. | PRO |
| `set_transition_effect` | Set an OpaqueBehavior effect on a Transition. | PRO |
| `create_activity` | Create a UML Activity owned by parent_id. | PRO |
| `create_action` | Create an Action inside an Activity. action_type: OpaqueAction (default), CallBehaviorAction, SendSignalAction. | PRO |
| `create_control_flow` | Create a ControlFlow edge between two ActivityNodes within an Activity. | PRO |
| `create_object_flow` | Create an ObjectFlow edge between two ActivityNodes within an Activity. | PRO |
| `create_requirement` | Create a SysML Requirement element under parent_id. | PRO |
| `create_proxy_port` | Create a SysML ProxyPort on a Block. | PRO |
| `create_full_port` | Create a SysML FullPort on a Block. | PRO |
| `create_flow_port` | Create a SysML FlowPort on a Block. | PRO |
| `add_refine` | Create a SysML Refine dependency from source to target. | PRO |
| `add_copy` | Create a SysML Copy dependency from source to target. | PRO |
| `add_trace` | Create a UML Trace dependency from source to target (StandardProfile). | PRO |
| `list_layout_styles` | List available auto-layout styles for a diagram. | FREE |
| `compare_layout_styles` | Compare how each auto-layout style would affect a diagram. | FREE |
| `get_edit_history` | Return the edit history (change log) for an element. | FREE |
| `create_association` | Create a UML Association between two classifiers. | PRO |
| `create_association_block` | Create a SysML Association Block (AssociationClass + Block stereotype). | PRO |
| `create_flow_specification` | Create a SysML FlowSpecification (Interface + FlowSpecification stereotype). | PRO |
| `create_flow_property` | Create a SysML FlowProperty. direction: in \ | out \ | PRO | `parent_id: str`, `name: str`, `direction: str` |
| `create_constraint_property` | Create a ConstraintProperty typed by a ConstraintBlock. | PRO |
| `set_encapsulated` | Set the isEncapsulated tagged value on a Block. value: 'true' or 'false'. | PRO |
| `set_item_flow_conveyed` | Set the conveyed Classifier on a SysML ItemFlow. | PRO |
| `create_interaction` | Create a UML Interaction (container for sequence diagram content). | PRO |
| `create_lifeline` | Create a Lifeline inside a UML Interaction. | PRO |
| `create_message` | Create a Message between two Lifelines in an Interaction. Creates send/receive occurrence specs automatically. | PRO |
| `create_combined_fragment` | Create a CombinedFragment in an Interaction. operator: alt \ | opt \ | break \ | par \ | seq \ | strict \ | neg. | PRO | `interaction_id: str`, `name: str`, `operator: str` |
| `get_standard_library_types` | Return the available standard library DataTypes from the open project. | FREE |

---

## Modify Tools

Element rename, delete, move, and property updates. Source: `modify_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `rename_element` | Rename a SysML v1 element. | PRO |
| `set_documentation` | Set the documentation (owned Comment body) of an element. | PRO |
| `delete_element` | Permanently delete an element from the model. | DANGEROUS |
| `move_element` | Move an element to a new parent (re-owner). | PRO |
| `set_type` | Set the type of a TypedElement (Property, Parameter, Port, etc.). | PRO |
| `set_multiplicity` | Set multiplicity bounds on a MultiplicityElement. Use -1 for upper=*. | PRO |
| `set_value` | Set the default value of a Property as a LiteralString. | PRO |
| `set_constraint` | Create a Constraint with an OpaqueExpression body on parent_id. | PRO | None = None` |
| `set_property` | Set a tagged value (stereotype property) on an element via TagsHelper. | PRO |
| `apply_stereotype` | Apply a stereotype to an element by its qualified name. | PRO |
| `remove_stereotype` | Remove a stereotype from an element by its qualified name. | PRO |
| `set_requirement_id` | Set the SysML requirement ID tagged value on a Requirement element. | PRO |
| `set_requirement_text` | Set the normative requirement text on a Requirement element. | PRO |
| `set_value_type_unit` | Set the unit of a SysML ValueType element. | PRO |
| `set_flow_direction` | Set the direction of a Parameter. Valid values: IN, OUT, INOUT, RETURN. | PRO |

---

## Relationship Tools

Requirement traceability and connector end management. Source: `relationship_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `add_satisfy` | Create a Satisfy relationship from a satisfying element to a requirement. | PRO |
| `add_verify` | Create a Verify relationship from a verifying element to a requirement. | PRO |
| `add_derive` | Create a DeriveReqt relationship between two requirements. | PRO |
| `set_connection_ends` | Set source and target ConnectorEnd roles on a Connector. | PRO |
| `add_dependency` | Create a UML Dependency between a client and supplier element. | PRO |

---

## Quality Tools

Model analysis, coverage, and traceability reporting. Source: `quality_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `impact_analysis` | Return elements that use or are used by the given element. | FREE |
| `validate_model` | Run built-in model validation and return any rule violations. | FREE |
| `check_requirement_coverage` | Return coverage statistics: how many requirements are satisfied/verified. | FREE |
| `check_documentation_coverage` | Return fraction of named elements that have documentation set. | FREE |
| `check_naming_conventions` | Return elements that violate UpperCamelCase / lowerCamelCase conventions. | FREE |
| `find_unused_types` | Return classifiers that are not used as a type anywhere in the model. | FREE |
| `find_duplicates` | Return elements that share the same type+name combination. | FREE |
| `export_requirements_matrix` | Return a full requirements traceability matrix with satisfy/verify links. | FREE |
| `trace_requirement` | Return full traceability chain for one requirement (derive, satisfy, verify). | FREE |
| `generate_model_summary` | Return a high-level summary of model element counts and coverage. | FREE |
| `get_model_metrics` | Return raw element counts broken down by UML/SysML type. | FREE |

---

## Diagram Tools

Diagram creation, symbol management, layout, and image export. Source: `diagram_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `create_diagram` | Create a SysML v1 diagram. Kinds: BDD, IBD, Parametric, Requirement, Activity, StateMachine, UseCase, Package, Sequence. | PRO |
| `list_diagrams` | List diagrams owned by a package or element. | FREE |
| `list_diagram_kinds` | Return supported diagram kinds for SysML v1. | FREE |
| `add_symbol` | Add an element symbol to a diagram. | PRO |
| `remove_symbol` | Remove an element symbol from a diagram. | PRO |
| `populate_diagram` | Add multiple element symbols to a diagram. | PRO |
| `auto_layout_diagram` | Apply Cameo's automatic layout to a diagram. | PRO |
| `list_diagram_symbols` | List all symbols currently in a diagram. | FREE |
| `export_diagram_image` | Export a diagram as a JPEG image (base64 encoded, max 1024px). Returns MCP ImageContent. | FREE |
| `list_layout_styles` | Return supported diagram layout styles. | FREE |
| `compare_layout_styles` | Compare available layout styles for a diagram. | FREE |
| `apply_custom_layout` | Apply a named layout style to a diagram. | PRO |
| `move_symbol` | Move a symbol to specific coordinates. | PRO |
| `resize_symbol` | Resize a symbol in a diagram. | PRO |
| `set_symbol_style` | Set visual style properties on a diagram symbol. | PRO |
| `set_compartment_visibility` | Show or hide a compartment on a symbol. | PRO |
| `add_path` | Add a relationship path to a diagram. | PRO |
| `route_path` | Set routing style for a relationship path. | PRO |
| `add_diagram_note` | Add a text note to a diagram. | PRO |

---

## Macro Tools

Direct JVM script execution. Source: `macro_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `execute_groovy` | Execute Groovy script inside CATIA Magic's JVM with full SysML v1 API access. Requires dev mode active on the plugin side. | DANGEROUS |

---

## V1 Vocabulary Tools

SysML v1 typed convenience wrappers over `create_element`. Source: `v1_tools.py`.

| Tool | Description | Tier |
|---|---|---|
| `create_block` | Create a SysML v1 Block under parent_id. | PRO |
| `create_part_property` | Create a PartProperty (typed composite part) under a Block. | PRO |
| `create_value_property` | Create a ValueProperty (scalar attribute) under a Block. | PRO |
| `create_reference_property` | Create a ReferenceProperty under a Block. | PRO |
| `create_interface_block` | Create a SysML InterfaceBlock under parent_id. | PRO |
| `create_value_type` | Create a SysML ValueType under parent_id. | PRO |
| `create_constraint_block` | Create a SysML ConstraintBlock under parent_id. | PRO |
| `create_use_case` | Create a UseCase element under parent_id. | PRO |
| `create_actor` | Create an Actor element under parent_id. | PRO |

---

> **Note on duplicates:** `list_layout_styles`, `compare_layout_styles`, and `get_edit_history` are registered in both `write_tools.py` and `diagram_tools.py`/`lifecycle_tools.py`. The 136 total above counts raw registrations. Unique tool names: 133.

<!-- total: 136 tools -->
