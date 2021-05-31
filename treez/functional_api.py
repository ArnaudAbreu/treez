"""
A module to implement useful function to handle trees.

Trees are stored as dictionaries.
"""
from typing import List, Sequence, Tuple, Optional, Union
import warnings
from .util import (
    Node,
    NodeProperties,
    NodeProperty,
    BinaryNodeProperty,
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
    InvalidNodeProps,
    UnrelatedNode,
    UnreachableAncestor,
    UnknownNodeProperty
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
        warnings.warn("Requested node {} is not in the parenthood.".format(node))
        return [node]
    root = node
    root_path = [node]
    while root in parents:
        root = parents[root]
        root_path.append(root)
    return root_path


def get_root_path_match(
    parents: Parenthood, node: Node, target: Node
) -> List[Node]:
    """
    Get path to root of a node in a tree.

    *************************************
    """
    if target not in parents:
        warnings.warn("Target node {} is not in the parenthood.".format(target))
        return get_root_path(parents, node)
    if node not in parents:
        warnings.warn("Requested node {} is not in the parenthood.".format(node))
        return []
    root = node
    root_path = [node]
    while root in parents:
        if root == target:
            return root_path
        root = parents[root]
        root_path.append(root)


def get_leaves_without_prop(
    children: Childhood,
    node: Node,
) -> List[Node]:
    """
    Get leaves of a node in a tree.

    *******************************
    """
    if node not in children:
        return [node]
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


def get_leaves_with_prop(
    children: Childhood,
    node: Node,
    prop: BinaryNodeProperty
) -> List[Node]:
    """
    Get leaves of a node in a tree.

    *******************************
    """
    if node not in prop:
        warnings.warn("Node {} does not have the property".format(node))
        return []
    if not prop[node]:
        warnings.warn("Root {} does not pass the property test.".format(node))
        return []
    if node not in children:
        warnings.warn("Children of Root {} does not pass the property.".format(node))
        return [node]
    no_lvs = [node]
    lvs = []
    while len(no_lvs) > 0:
        new_no_lvs = []
        for n in no_lvs:
            if n in prop:
                if prop[n]:
                    if n in children:
                        candidates = []
                        for c in children[n]:
                            if c in prop:
                                if prop[c]:
                                    candidates.append(c)
                        new_no_lvs += candidates
                        if len(candidates) == 0:
                            lvs.append(n)
                    else:
                        lvs.append(n)
            else:
                warnings.warn("Node {} does not have the property".format(node))
        no_lvs = new_no_lvs
    return lvs


def get_leaves(
    children: Childhood,
    node: Node,
    prop: Optional[BinaryNodeProperty] = None
) -> List[Node]:
    """
    Get leaves of a node in a tree.

    *******************************
    """
    if prop is None:
        return get_leaves_without_prop(children, node)
    return get_leaves_with_prop(children, node, prop)


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
            props["size"][rn1] = s1
        if rn2 in props["size"]:
            s2 = props["size"][rn2]
        else:
            s2 = size[n2]
            props["size"][rn2] = s2
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


def _expand_on_property(
    cut: List[Node],
    children: Childhood,
    prop: NumericalNodeProperty,
    threshold: Union[int, float]
) -> List[Node]:
    """Create a new tree by cutting based on property threshold."""
    candidates = []
    expansion = []
    for node in cut:
        if node in children:
            candidates += children[node]
    for candidate in candidates:
        if candidate in prop:
            if prop[candidate] >= threshold:
                expansion.append(candidate)
    return expansion


def cut_on_property(
    parents: Parenthood,
    children: Childhood,
    prop: NumericalNodeProperty,
    threshold: Union[int, float]
) -> List[Node]:
    """Produce a list of authorized nodes given a property threshold."""
    root = get_root(parents)
    cut = set()
    remaining = [root]
    while len(remaining) > 0:
        cut |= set(remaining)
        remaining = _expand_on_property(remaining, children, prop, threshold)
    return list(cut)


def common_ancestor(
    parents: Parenthood,
    node1: Node,
    node2: Node
) -> Node:
    """Get the common ancestor of two nodes and store their distances to him."""
    if node1 in parents and node2 in parents:
        rp1 = get_root_path(parents, node1)
        rp2 = get_root_path(parents, node2)
        if len(set(rp1) & set(rp2)) > 0:
            for node in rp1:
                if node in rp2:
                    return node
        raise UnrelatedNode(
            "Nodes {} and {} have no common ancestors!!!".format(node1, node2)
        )
    raise UnrelatedNode(
        "One of the provided nodes: ({}, {}) has no parent...".format(
            node1, node2
        )
    )


def edge_dist(
    parents: Parenthood,
    node1: Node,
    node2: Node
) -> int:
    """Return the number of edges to go from node1 to node2 (by common ancestor)."""
    ancestor = common_ancestor(parents, node1, node2)
    rpm1 = get_root_path_match(parents, node1, ancestor)
    rpm2 = get_root_path_match(parents, node2, ancestor)
    return len(set(rpm1) | set(rpm2))


def weighted_dist(
    parents: Parenthood,
    weights: NumericalNodeProperty,
    node1: Node,
    node2: Node
) -> float:
    """Return the number of edges to go from node1 to node2 (by common ancestor)."""
    ancestor = common_ancestor(parents, node1, node2)
    rpm1 = get_root_path_match(parents, node1, ancestor)
    rpm2 = get_root_path_match(parents, node2, ancestor)
    nodes_in_path = (set(rpm1) | set(rpm2))
    nodes_in_path.discard(node1)
    nodes_in_path.discard(node2)
    dist = 0.
    for node in nodes_in_path:
        if node not in weights:
            raise UnknownNodeProperty(
                "Missing weight for node {} to compute a weighted distance!!!".format(node)
            )
        dist += weights[node]
    # minus 1 otherwise ancestor is counted twice
    return dist
