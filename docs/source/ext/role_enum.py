from docutils import nodes
from sphinx import addnodes
from sphinx.domains.index import IndexRole
from sphinx.util.nodes import process_index_entry


def make_index(id: str, *entries: str):
    node = addnodes.index()
    node["entries"] = []
    for entry in entries:
        node["entries"].extend(process_index_entry(entry, id))
    return node


class EnumRole(IndexRole):
    """
    Utility role to assist in enumeration indexing within ``.. list-table``.

    .. note::

      The ``.. list-table`` approach should preferably be replaced
      with a custom directive, and the directive should handle the indexing.
    """

    def _ensure_header(self, section) -> str:
        """Ensure that the enum category is included in the index and return its name."""
        title_node = section[0]
        if not isinstance(title_node, nodes.title):
            raise ValueError(f"Expected title node, got {title_node!r}")

        title = title_node.astext()
        prev_node = section.previous_sibling()
        if (
            isinstance(prev_node, addnodes.index)
            and prev_node["ids"][0] == section["ids"][0]
        ):
            return title

        # add index node
        index = make_index(
            section["ids"][0],
            f"single: {title}",
            f"single: Enumerations; {title}",
        )
        section.replace_self([index, section])
        return title

    def run(self):
        section_node = None
        for s in self.inliner.document._fast_findall(nodes.section):
            section_node = s
        header = self._ensure_header(section_node)
        title = self.title
        target_id = f"enum-{nodes.make_id(header)}_{nodes.make_id(title)}"
        target_node = nodes.target("", "", ids=[target_id])
        self.inliner.document.note_explicit_target(target_node)
        index_node = make_index(
            target_id,
            f"single: {header}; {title}",
        )
        index_node["inline"] = True

        self.set_source_info(target_node)
        self.set_source_info(index_node)
        text = nodes.inline(title, title, classes=["enum-entry"])
        return [index_node, target_node, text], []


import sphinx.application


def setup(app: sphinx.application.Sphinx):
    app.add_role("enum", EnumRole())
