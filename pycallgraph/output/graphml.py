from __future__ import division

import pyed

from ..color import Color
from .output import Output


class GraphmlOutput(Output):
    def __init__(self, **kwargs):
        self.output_file = "pycallgraph.graphml"
        self.output_type = "graphml"
        self.font_name = "Verdana"
        self.font_size = 7
        self.group_border_color = Color(0, 0, 0, 0.8)

        self.graph = pyed.Graph()
        # Get full list of nodes by their name to reference to them later (link them in group)
        self.nodes = {}

        Output.__init__(self, **kwargs)

        self.prepare_graph_attributes()

    @classmethod
    def add_arguments(cls, subparsers, parent_parser, usage):
        defaults = cls()

        subparser = subparsers.add_parser(
            "graphml",
            help="GraphML generation",
            parents=[parent_parser],
            usage=usage,
        )

        subparser.add_argument(
            "--font-name",
            type=str,
            default=defaults.font_name,
            help="Name of the font to be used",
        )

        subparser.add_argument(
            "--font-size",
            type=int,
            default=defaults.font_size,
            help="Size of the font to be used",
        )

        cls.add_output_file(subparser, defaults, "The generated GraphML file")

    def prepare_graph_attributes(self):
        self.node_style = {"shape": "rectangle", "title_style": {"fontFamily": self.font_name,
                                                                 "fontSize": str(self.font_size)}}
        self.edge_style = {"label_style": {"fontFamily": self.font_name, "fontSize": str(self.font_size),
                                           "backgroundColor": "#ffffff"}}
        self.group_style = {"title_style": {"fontStyle": "bold"}, "border_color": self.group_border_color.rgba_web()}

    def done(self):
        self.generate()

        self.graph.write_graph(self.output_file)

        self.verbose(
            f"Generated {self.output_file} with {len(self.processor.func_count)} nodes."
        )

    def generate(self):
        """Returns a string with the contents of a DOT file for Graphviz to
        parse.
        """
        # self.generate_attributes()
        self.generate_nodes()
        self.generate_edges()
        self.generate_groups()

    def generate_groups(self):
        if not self.processor.config.groups:
            return ""

        for group, nodes in self.processor.groups():
            grp_node = self.graph.add_group(group, **self.group_style)

            for node in nodes:
                node_obj = self.nodes[node.name]
                grp_node.link_node(node_obj)

    def generate_nodes(self):
        for node in self.processor.nodes():
            node_obj = self.graph.add_node(pyed.ShapeNode, self.node_label_func(node),
                                background=self.node_color_func(node).rgba_web(), **self.node_style)
            self.nodes[node.name] = node_obj

    def node_label(self, node):
        """
        Overwrite the Output method to have a simpler output.

        r'' is not working with graphml anyway, and I have no newline in the output (in the event we revert to the old
        display, I still have to overwrite here to get rid of the raw string and take a normal string instead.
        """
        return node.name

    def generate_edges(self):

        for edge in self.processor.edges():
            node1 = self.nodes[edge.src_func]
            node2 = self.nodes[edge.dst_func]
            self.graph.add_edge(node1, node2, label=self.edge_label_func(edge),
                                color=self.edge_color_func(edge).rgba_web(), **self.edge_style)
