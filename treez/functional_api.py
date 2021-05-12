"""
A module to implement useful function to handle trees.

Trees are stored as dictionaries.
"""
from typing import List, Sequence, Tuple, Optional
from .util import (
    Node,
    NodeProperties,
    NodeProperty,
    SymbolicNodeProperty,
    NumericalNodeProperty,
    Parenthood,
    Childhood,
    Edge,
    EdgeProperties,
    EdgeProperty,
    NumericalEdgeProperty,
    SymbolicEdgeProperty,
    UFDS,
    InvalidEdgeProps,
    InvalidNodeProps
)
import json


def get_root(parents: Parenthood, node: Node = None) -> Node:
    """
    Get root of a node in a tree.

    *****************************
    """
    if node is None:
        for k, v in parents.items():
            node = k
            return get_root(parents, k)
    if node not in parents:
        return node
    root = node
    while root in parents:
        root = parents[root]
    return root


def get_root_path(parents: Parenthood, node: Node) -> List[Node]:
    """
    Get path to root of a node in a tree.

    *************************************
    """
    if node not in parents:
        return [node]
    root = node
    root_path = [node]
    while root in parents:
        root = parents[root]
        root_path.append(root)
    return root_path


def get_leaves(children: Childhood, node: Node) -> List[Node]:
    """
    Get leaves of a node in a tree.

    *******************************
    """
    if node not in children:
        return node
    no_lvs = [node]
    lvs = []
    while len(no_lvs) > 0:
        new_no_lvs = []
        for n in no_lvs:
            if n in children:
                for c in children[n]:
                    new_no_lvs.append(c)
            else:
                lvs.append(n)
        no_lvs = new_no_lvs
    return lvs


def kruskal_edges(
    edges: Sequence[Edge], weights: NumericalEdgeProperty
) -> Sequence[Edge]:
    """
    Yield kruskal edges, given a list of edges.

    ********************************************
    """
    # create Union-Find data structure
    components = UFDS()
    # edges are sorted by non-decreasing order of dissimilarity
    edges = sorted(edges, key=lambda x: weights[x])
    k_edges = []
    k_weights = []

    for edge in edges:
        # nodes in involved in the edge
        n1, n2 = edge
        # roots of nodes in the Union-Find
        rn1 = components.get_root(n1)
        rn2 = components.get_root(n2)
        # if components are differents
        if rn1 != rn2:
            components.union(edge)
            k_edges.append(edge)
            k_weights.append(weights[edge])
    return k_edges, k_weights


def kruskal_tree(
    edges: Sequence[Edge],
    weights: NumericalEdgeProperty,
    size: NumericalNodeProperty
) -> Tuple[Parenthood, Childhood, NumericalNodeProperty]:
    """
    Create parents an children relationships from kruskal edges.

    ***********************************************************
    """
    parents = dict()
    children = dict()
    props = {"weights": dict(), "size": dict()}
    k_edges, k_weights = kruskal_edges(edges, weights)
    max_node = 2 * len(k_edges)
    for edge, weight in zip(k_edges, k_weights):
        n1, n2 = edge
        rn1 = get_root(parents, n1)
        rn2 = get_root(parents, n2)
        if rn1 in props["size"]:
            s1 = props["size"][rn1]
        else:
            s1 = size[n1]
        if rn2 in props["size"]:
            s2 = props["size"][rn2]
        else:
            s2 = size[n2]
        # since it is already a spanning tree,
        # I know rn1 and rn2 have different roots
        parents[rn1] = max_node
        parents[rn2] = max_node
        children[max_node] = [rn1, rn2]
        props["weights"][max_node] = weight
        props["size"][max_node] = s1 + s2

        max_node += 1
    return parents, children, props


def tree_to_json(
    nodes: Sequence[Node],
    parents: Parenthood,
    children: Childhood,
    jsonfile: str,
    nodeprops: Optional[NodeProperties] = None,
    edgeprops: Optional[EdgeProperties] = None
):
    """Store a jsonified tree to a json file."""
    output_dict = dict()
    output_dict["nodes"] = nodes
    output_dict["parents"] = parents
    output_dict["children"] = children
    output_dict["nodeprops"] = dict()
    output_dict["edgeprops"] = dict()
    if nodeprops is not None:
        if isinstance(nodeprops, dict):
            for k, v in nodeprops.items():
                output_dict["nodeprops"][k] = v
        else:
            raise InvalidNodeProps(
                "Invalid node props, "
                "expected {} but got {}".format(dict, type(nodeprops))
            )
    if edgeprops is not None:
        if isinstance(edgeprops, dict):
            for k, v in edgeprops.items():
                output_dict["edgeprops"][k] = v
        else:
            raise InvalidEdgeProps(
                "Invalid node props, "
                "expected {} but got {}".format(dict, type(edgeprops))
            )
    json_dict = json.dumps(output_dict)
    with open(jsonfile, "w") as outputjson:
        outputjson.write(json_dict)
