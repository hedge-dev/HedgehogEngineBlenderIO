
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective


class refbox(nodes.Admonition, nodes.Element):
    pass


def visit_refbox_node(self, node):
    self.visit_admonition(node)


def depart_refbox_node(self, node):
    self.depart_admonition(node)


class ReferenceDirective(BaseAdmonition, SphinxDirective):
    node_class = refbox
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'class': directives.class_option,
        'name': directives.unchanged,
    }

    def run(self):
        if not self.options.get('class'):
            self.options['class'] = ['refbox']

        (reference,) = super().run()
        if isinstance(reference, nodes.system_message):
            return [reference]
        elif isinstance(reference, refbox):
            reference.insert(0, nodes.title(text=_('Reference')))
            reference['docname'] = self.env.docname
            self.add_name(reference)
            self.set_source_info(reference)
            self.state.document.note_explicit_target(reference)
            return [reference]
        else:
            raise RuntimeError  # never reached here


def setup(app):
    app.add_node(
        refbox,
        html=(visit_refbox_node, depart_refbox_node),
        latex=(visit_refbox_node, depart_refbox_node),
        text=(visit_refbox_node, depart_refbox_node),
        man=(visit_refbox_node, depart_refbox_node),
        texinfo=(visit_refbox_node, depart_refbox_node),
    )

    app.add_directive('reference', ReferenceDirective)

    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
