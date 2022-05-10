#!/usr/bin/env python3
from typing import cast

from src.paddle_api_impl import project_pb2 as project_api
from src.paddle_api.config_spec import CompositeSpecNode, ArraySpecNode, StringSpecNode, BooleanSpecNode, IntegerSpecNode


def to_composite_spec(protobuf: project_api.CompositeSpecNode) -> CompositeSpecNode:
    root = CompositeSpecNode(title=protobuf.title, description=protobuf.description)
    root.required.extend(protobuf.required)
    for (name, node) in protobuf.properties:
        if isinstance(node, project_api.CompositeSpecNode):
            root.properties[name] = to_composite_spec(node)
        elif isinstance(node, project_api.ArraySpecNode):
            root.properties[name] = to_array_spec(node)
        elif isinstance(node, project_api.StringSpecNode):
            str_node = StringSpecNode(title=node.title, description=node.description)
            str_node.valid_values.extend(node.valid)
            root.properties[name] = str_node
        elif isinstance(node, project_api.IntegerSpecNode):
            int_node = IntegerSpecNode(title=node.title, description=node.description)
            int_node.valid_values.extend(node.valid)
            root.properties[name] = int_node
        elif isinstance(node, project_api.BooleanSpecNode):
            bool_node = BooleanSpecNode(title=node.title, description=node.description)
            bool_node.valid_values.extend(node.valid)
            root.properties[name] = bool_node

    root.valid_specs.extend(map(lambda v: to_composite_spec(v), protobuf.valid))
    return root


def to_array_spec(protobuf: project_api.ArraySpecNode) -> ArraySpecNode:
    array_node = ArraySpecNode(title=protobuf.title, description=protobuf.description)
    if isinstance(protobuf.items, project_api.CompositeSpecNode):
        array_node.items = to_composite_spec(protobuf.items)
    elif isinstance(protobuf.items, project_api.ArraySpecNode):
        array_node.items = to_array_spec(protobuf.items)
    elif isinstance(protobuf.items, project_api.StringSpecNode):
        str_node = StringSpecNode(title=protobuf.items.title, description=protobuf.items.description)
        str_node.valid_values.extend(protobuf.items.valid)
        array_node.items = str_node
    elif isinstance(protobuf.items, project_api.IntegerSpecNode):
        int_node = IntegerSpecNode(title=protobuf.items.title, description=protobuf.items.description)
        int_node.valid_values.extend(protobuf.items.valid)
        array_node.items = int_node
    elif isinstance(protobuf.items, project_api.BooleanSpecNode):
        bool_node = BooleanSpecNode(title=protobuf.items.title, description=protobuf.items.description)
        bool_node.valid_values.extend(protobuf.items.valid)
        array_node.items = bool_node
    return array_node


def to_protobuf_composite(composite_spec_node: CompositeSpecNode) -> project_api.CompositeSpecNode:
    root = project_api.CompositeSpecNode(title=composite_spec_node.title, description=composite_spec_node.description)
    root.required.extend(composite_spec_node.required)
    for (name, node) in composite_spec_node.properties:
        if isinstance(node, CompositeSpecNode):
            root.properties[name] = to_protobuf_composite(node)
        elif isinstance(node, ArraySpecNode):
            root.properties[name] = to_protobuf_array(node)
        elif isinstance(node, StringSpecNode):
            str_node = project_api.StringSpecNode(title=node.title, description=node.description)
            str_node.valid.extend(node.valid_values)
            root.properties[name] = str_node
        elif isinstance(node, IntegerSpecNode):
            int_node = project_api.IntegerSpecNode(title=node.title, description=node.description)
            int_node.valid.extend(node.valid_values)
            root.properties[name] = int_node
        elif isinstance(node, BooleanSpecNode):
            bool_node = project_api.BooleanSpecNode(title=node.title, description=node.description)
            bool_node.valid.extend(node.valid_values)
            root.properties[name] = bool_node

    root.valid.extend(map(lambda v: to_protobuf_composite(v), composite_spec_node.valid_specs))
    return root


def to_protobuf_array(array_spec_node: ArraySpecNode) -> project_api.ArraySpecNode:
    array_node = project_api.ArraySpecNode(title=array_spec_node.title, description=array_spec_node.description)
    if isinstance(array_spec_node.items, CompositeSpecNode):
        array_node.items = to_protobuf_composite(cast(CompositeSpecNode, array_spec_node.items))
    elif isinstance(array_spec_node.items, ArraySpecNode):
        array_node.items = to_protobuf_array(cast(ArraySpecNode, array_spec_node.items))
    elif isinstance(array_spec_node.items, StringSpecNode):
        str_node = project_api.StringSpecNode(title=array_spec_node.items.title, description=array_spec_node.items.description)
        str_node.valid.extend(cast(StringSpecNode, array_spec_node.items).valid_values)
        array_node.items = str_node
    elif isinstance(array_spec_node.items, IntegerSpecNode):
        int_node = project_api.IntegerSpecNode(title=array_spec_node.items.title, description=array_spec_node.items.description)
        int_node.valid_values.extend(cast(IntegerSpecNode, array_spec_node.items).valid_values)
        array_node.items = int_node
    elif isinstance(array_spec_node.items, BooleanSpecNode):
        bool_node = project_api.BooleanSpecNode(title=array_spec_node.items.title, description=array_spec_node.items.description)
        bool_node.valid_values.extend(cast(BooleanSpecNode, array_spec_node.items).valid_values)
        array_node.items = bool_node
    return array_node
