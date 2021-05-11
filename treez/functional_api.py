"""
A module to implement useful function to handle trees.

Trees are stored as dictionaries.
"""
from typing import List, Sequence, Tuple
from .util import (
    NodeId,
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
    UFDS
)


def get_root(parents: Parenthood, node: NodeId = None) -> NodeId:
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


def get_root_path(parents: Parenthood, node: NodeId) -> List[NodeId]:
    """
    Get path to root of a node in a tree.

    *****************************
    """
    if node not in parents:
        return [node]
    root = node
    root_path = [node]
    while root in parents:
        root = parents[root]
        root_path.append(root)
    return root_path


def get_leaves(children: Childhood, node: NodeId) -> List[NodeId]:
    """
    Get leaves of a node in a tree.

    *****************************
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
    return k_edges


def kruskal_tree(
    edges: Sequence[Edge], weights: NumericalEdgeProperty
) -> Tuple[Parenthood, Childhood]:
    """
    Create parents an children relationships from kruskal edges.

    ***********************************************************
    """
    parents = dict()
    children = dict()
    k_edges = kruskal_edges(edges, weights)
    max_node = max([max(edge) for edge in k_edges]) + 1
    for edge in k_edges:
        n1, n2 = edge
        rn1 = get_root(parents, n1)
        rn2 = get_root(parents, n2)
        # since it is already a spanning tree,
        # I know rn1 and rn2 have different roots
        parents[rn1] = max_node
        parents[rn2] = max_node

        children[max_node] = [rn1, rn2]

        max_node += 1
    return parents, children
