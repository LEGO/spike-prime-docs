import re
from docutils import nodes
from docutils.statemachine import ViewList, StringList
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.util.docutils import SphinxDirective
from sphinx.application import Sphinx
from sphinx.util.nodes import (
    make_refnode,
    nested_parse_with_titles,
    process_index_entry,
)


class MessageData:
    def __init__(self, name, id, is_device_message):
        self.name = name
        self.id_dec = id
        self.id_hex = f"0x{id:0{2}X}"
        self.is_device_message = is_device_message


class quickref(nodes.General, nodes.Element):
    pass


class QuickRefDirective(SphinxDirective):
    def run(self):
        return [quickref("")]


class MessageDirective(SphinxDirective):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "id": lambda x: int(x),
        "device-message": directives.flag,
    }

    message_data: MessageData = None

    @property
    def hex_id(self):
        return self.message_data.id_hex

    @property
    def message_name(self):
        return self.message_data.name

    @property
    def is_device_message(self):
        return self.message_data.is_device_message

    def _make_index(self, target_id):
        entries: list[str] = []
        if self.is_device_message:
            entries.append(f"single: DeviceNotification; {self.message_name}")
        else:
            entries.append(f"single: {self.message_name}")
            entries.append(f"single: Messages; {self.message_name}")
        index = addnodes.index("", entries=[])
        for entry in entries:
            index["entries"].extend(process_index_entry(entry, target_id))
        return index

    def _render(self, lines: list[str]) -> list[nodes.Node]:
        vl = StringList()
        for line in lines:
            vl.append(line, "")
        parent = nodes.Element("")
        self.state.nested_parse(vl, 0, parent)
        return parent.children

    def _make_message_id_field(self) -> nodes.field:
        node = nodes.field("")
        node += nodes.field_name("", "uint8")
        node += nodes.field_body("")
        node[1].extend(self._render([f"Message type (``{self.hex_id}``)"]))
        return node

    def _parse_field_format(self, fmt: str):
        int_match = re.search(r"^u?int(\d+)$", fmt)
        if int_match is not None:
            return f":term:`{fmt} <int>`"

        array_match = re.search(r"^u?int(\d+)\[([^]]*)\]$", fmt)
        if array_match is not None:
            return f":term:`{fmt} <array>`"

        string_match = re.search(r"^string\[([^]]*)\]$", fmt)
        if string_match is not None:
            return f":term:`{fmt} <null-terminated string>`"

        return fmt

    def _make_table_from_fields(self, field_list: nodes.field_list) -> nodes.table:
        id_field = self._make_message_id_field()
        field_rows = [id_field] + field_list

        table = nodes.table("", classes=["colwidths-given", "first-col-right"])
        columns = (("Format", 1), ("Description", 4))
        tgroup = nodes.tgroup("", cols=len(columns))
        tgroup.extend([nodes.colspec("", colwidth=c[1]) for c in columns])
        table += tgroup
        thead = nodes.thead("")
        tgroup += thead
        tbody = nodes.tbody("")
        tgroup += tbody

        rhead = nodes.row("")
        rhead.extend(
            [nodes.entry("", nodes.paragraph("", c)) for c in ["Format", "Description"]]
        )
        thead += rhead

        for field in field_rows:
            row = nodes.row("")
            fmt_display = self._parse_field_format(field[0].astext())

            row += nodes.entry("", *self._render([fmt_display]))
            row += nodes.entry("", *field[1].children)

            tbody += row

        return table

    def run(self) -> list[nodes.Node]:
        self.message_data = MessageData(
            name=self.arguments[0],
            id=self.options["id"],
            is_device_message="device-message" in self.options,
        )
        message_header = f"``{self.hex_id}`` {self.message_name}"

        content_node: nodes.Element = nodes.section()
        content_node.document = self.state.document

        content = ViewList(self.content, source="")
        content.insert(
            0,
            StringList(
                [
                    message_header,
                    "*" * len(message_header),
                    "",
                ]
            ),
        )
        nested_parse_with_titles(self.state, content, content_node, self.content_offset)
        section_node = content_node.next_node(nodes.section)
        if self.is_device_message:
            section_node["classes"].append("device-message")

        field_list = content_node[0].next_node(nodes.field_list)
        if field_list is None:
            field_list = nodes.field_list()
            content_node[0] += field_list
        table = self._make_table_from_fields(field_list)
        field_list.replace_self(table)

        ret: list[nodes.Node] = []
        ret.append(self._make_index(section_node["ids"][0]))
        ret.extend(content_node.children)

        if not hasattr(self.env, "message_all_messages"):
            self.env.message_all_messages = []

        self.env.message_all_messages.append(
            {
                "docname": self.env.docname,
                "lineno": self.lineno,
                "target": section_node,
                "data": self.message_data,
            }
        )

        return ret


def purge_messages(app, env, docname):
    if not hasattr(env, "message_all_messages"):
        return
    env.message_all_messages = [
        message for message in env.message_all_messages if message["docname"] != docname
    ]


def merge_messages(app, env, docnames, other):
    if not hasattr(env, "message_all_messages"):
        env.message_all_messages = []
    if hasattr(other, "message_all_messages"):
        env.message_all_messages.extend(other.message_all_messages)


def process_message_nodes(app, doctree, fromdocname):
    env = app.builder.env
    if not hasattr(env, "message_all_messages"):
        env.message_all_messages = []

    for node in doctree.findall(quickref):
        # only quickref messages in the same document
        doc_messages = [
            message
            for message in env.message_all_messages
            if message["docname"] == fromdocname
        ]
        if not doc_messages:
            node.replace_self([])
            continue

        quickref_columns = (
            ("Type ID\n(base 10)", 1),
            ("Type ID\n(base 16)", 1),
            ("Message", 6),
        )
        table = nodes.table("", classes=["colwidths-given", "message-quickref"])
        tgroup = nodes.tgroup("", cols=len(quickref_columns))
        tgroup.extend([nodes.colspec("", colwidth=c[1]) for c in quickref_columns])
        table += tgroup
        thead = nodes.thead("")
        tgroup += thead
        tbody = nodes.tbody("")
        tgroup += tbody

        rhead = nodes.row("")
        rhead.extend(
            [
                nodes.entry("", *[nodes.paragraph("", l) for l in c[0].split("\n")])
                for c in quickref_columns
            ]
        )
        thead += rhead

        for message in doc_messages:
            row = nodes.row("")
            row += nodes.entry("", nodes.literal("", str(message["data"].id_dec)))
            row += nodes.entry("", nodes.literal("", message["data"].id_hex))
            p = nodes.paragraph("")
            p += make_refnode(
                app.builder,
                fromdocname,
                message["docname"],
                message["target"]["ids"][0],
                nodes.Text(message["data"].name),
                message["data"].name,
            )
            row += nodes.entry("", p)
            tbody += row

        node.replace_self(table)


def setup(app: Sphinx):
    app.add_node(quickref)
    app.add_directive("message-quickref", QuickRefDirective)
    app.add_directive("message", MessageDirective)

    app.connect("env-purge-doc", purge_messages)
    app.connect("env-merge-info", merge_messages)
    app.connect("doctree-resolved", process_message_nodes)
