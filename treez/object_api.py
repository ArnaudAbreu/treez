"""Just a bunch of useful classes."""
from typing import List, Sequence, Tuple, Optional, Union
import json
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
    UndefinedParenthood,
    UndefinedChildhood,
    UnknownNodeProperty,
    InvalidNodeId
)
from .functional_api import (
    get_root as _get_root,
    get_root_path as _get_root_path,
    get_root_path_match as _get_root_path_match,
    get_leaves as _get_leaves,
    tree_to_json as _tree_to_json,
    kruskal_tree as _kruskal_tree,
    cut_on_property as _cut_on_property,
    common_ancestor as _common_ancestor,
    edge_dist as _edge_dist,
    weighted_dist as _weighted_dist
)
import ast


class Tree(object):
    """Object to handle trees."""

    def __init__(
        self,
        nodes: Sequence[Node] = None,
        parents: Parenthood = None,
        children: Childhood = None,
        nodeprops: NodeProperties = None,
        edgeprops: EdgeProperties = None,
        jsonfile: str = None
    ):
        """Init tree object."""
        self.nodes = nodes
        self.parents = parents
        self.children = children
        self.nodeprops = nodeprops
        self.edgeprops = edgeprops
        if jsonfile is not None:
            self.from_json(jsonfile)

    def get_root(self, node: Node = None) -> Node:
        """Give root of the tree."""
        if self.parents is not None:
            return _get_root(self.parents, node)
        raise UndefinedParenthood(
            "Parenthood of the tree was not defined, "
            "please build the tree before use."
        )

    def get_root_path(self, node: Node) -> List[Node]:
        """Get path to root of the tree."""
        if self.parents is not None:
            return _get_root_path(self.parents, node)
        raise UndefinedParenthood(
            "Parenthood of the tree was not defined, "
            "please build the tree before use."
        )

    def get_leaves(
        self,
        node: Node,
        prop: Optional[BinaryNodeProperty] = None
    ) -> List[Node]:
        """Get leaves of a node."""
        if self.children is not None:
            return _get_leaves(self.children, node, prop)
        raise UndefinedChildhood(
            "Childhood of the tree was not defined, "
            "please build the tree before use."
        )

    def to_json(self, jsonfile):
        """Store the tree to json file."""
        _tree_to_json(
            self.nodes,
            self.parents,
            self.children,
            jsonfile,
            self.nodeprops,
            self.edgeprops
        )

    def from_json(self, jsonfile):
        """Create the tree from a json file."""
        # Keep in mind that json keys have to be str.
        # In treez framework, they can be python object as well
        # We use ast to parse the str to a python object before

        # This behaviour might limit even more the types of
        # parenthood/childhood/props keys when using treez...
        with open(jsonfile, "r") as jf:
            json_dict = json.load(jf)
        for k, v in json_dict.items():
            if k == "nodes":
                self.nodes = v
            if k == "parents":
                # Dict[Node, Node]
                self.parents = dict()
                for nodein, nodeout in v.items():
                    try:
                        nodekey = ast.literal_eval(nodein)
                        self.parents[nodekey] = nodeout
                    except (ValueError, SyntaxError):
                        self.parents[nodein] = nodeout
            if k == "children":
                # Dict[Node, List[Node]]
                self.children = dict()
                for nodein, nodeout in v.items():
                    try:
                        nodekey = ast.literal_eval(nodein)
                        self.children[nodekey] = nodeout
                    except (ValueError, SyntaxError):
                        self.children[nodein] = nodeout
                    # nodekey = ast.literal_eval(nodein)
                    # self.children[nodekey] = nodeout
            if k == "edgeprops":
                self.edgeprops = dict()
                for name, edgeprop in v.items():
                    self.edgeprops[name] = dict()
                    for edgein, edgeout in edgeprop.items():
                        try:
                            edgekey = ast.literal_eval(edgein)
                            self.edgeprops[name][edgekey] = edgeout
                        except (ValueError, SyntaxError):
                            self.edgeprops[name][edgein] = edgeout
            if k == "nodeprops":
                self.nodeprops = dict()
                for name, nodeprop in v.items():
                    self.nodeprops[name] = dict()
                    for nodein, nodeout in nodeprop.items():
                        try:
                            nodekey = ast.literal_eval(nodein)
                            self.nodeprops[name][nodekey] = nodeout
                        except (ValueError, SyntaxError):
                            self.nodeprops[name][nodein] = nodeout

    def build_kruskal(
        self, edges: Sequence[Edge],
        weights: NumericalEdgeProperty,
        size: NumericalNodeProperty
    ):
        """Build tree with kruskal algorithm from graph edges."""
        k_parents, k_children, k_props = _kruskal_tree(edges, weights, size)
        self.parents = k_parents
        self.children = k_children
        k_nodes = set(k_parents.keys())
        # root can be missing
        k_nodes.add(self.get_root())
        self.nodes = list(k_nodes)
        self.nodeprops = k_props

    def cut_on_property(
        self,
        cut_name: str,
        prop: str,
        threshold: Union[int, float]
    ):
        """
        Produce a list of authorized nodes given a property threshold.

        Set a new property to these nodes.
        """
        if prop in self.nodeprops:
            node_of_interest = _cut_on_property(
                self.parents,
                self.children,
                self.nodeprops[prop],
                threshold
            )
            cut = dict()
            for node in self.nodes:
                if node in node_of_interest:
                    cut[node] = True
                else:
                    cut[node] = False
            self.nodeprops[cut_name] = cut

        else:
            raise UnknownNodeProperty(
                "Property {}"
                " is not in the tree properties: {}".format(
                    prop, list(self.nodeprops.keys())
                )
            )

    def common_ancestor(
        self,
        node1: Node,
        node2: Node
    ) -> Node:
        """Return the common ancestor of node1 and node2."""
        return _common_ancestor(self.parents, node1, node2)

    def edge_dist(
        self,
        node1: Node,
        node2: Node
    ) -> int:
        """Return the number of edges to go from node1 to node2 (by common ancestor)."""
        return _edge_dist(self.parents, node1, node2)

    def weighted_dist(
        self,
        weights: Union[NumericalNodeProperty, str],
        node1: Node,
        node2: Node
    ) -> float:
        """Return the number of edges to go from node1 to node2 (by common ancestor)."""
        if isinstance(weights, str):
            if weights in self.nodeprops:
                return _weighted_dist(
                    self.parents, self.nodeprops[weights], node1, node2
                )
            raise InvalidNodeProps(
                "Property {} is not in tree properties: {}".format(
                    weights, self.nodeprops
                )
            )
        if isinstance(weights, dict):
            return _weighted_dist(self.parents, weights, node1, node2)
        raise InvalidNodeProps(
            "Provided property is not a valid property. "
            "Expected {} or {}, got {}".format(dict, str, type(weights))
        )
