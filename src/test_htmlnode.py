import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType 
from parsing import p_text_node_to_html_node
from conversion import md_to_html


class TestHTMLNode(unittest.TestCase):

    def test_empty_html_node(self):
        node  = HTMLNode()
        self.assertEqual(node.tag, None)
        self.assertEqual(node.value, None)
        self.assertEqual(node.children, None)
        self.assertEqual(node.props, None)

    def test_child_node_exists(self):
        node  = HTMLNode("h", "bogg", [], {"great": "yes"})
        node2  = HTMLNode("h", "bogg", [node], {"great": "yes"})
        self.assertIsInstance(node2.children[0], HTMLNode)

    def test_empty_props(self):
        node  = HTMLNode("h", "bogg", [])
        output = node.props_to_html()
        self.assertEqual(output, "")

    def test_repr(self):
        node  = HTMLNode("h", "bogg", [])
        output = node.__repr__()
        self.assertIn(".---HTMLNode---.", output)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "click me", {"href": "www.internet.gov"})
        self.assertEqual(node.to_html(), '<a href="www.internet.gov">click me</a>')

    def test_leaf_to_html_img(self):
        node = LeafNode("img", "", {"src": "url/of/image.jpg"})
        self.assertEqual(node.to_html(), '<img src="url/of/image.jpg"></img>')

    def test_leaf_to_html_img_alt(self):
        node = LeafNode("img", "", {"src": "url/of/image.jpg", "alt": "amazing image do not scrape it"})
        self.assertEqual(node.to_html(), '<img src="url/of/image.jpg" alt="amazing image do not scrape it"></img>')

    def test_parent_node(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )

        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_empty_children(self):
        try:
            node = ParentNode('p', [])
            node.to_html()
        except ValueError as e:
            self.assertEqual(f'{e}', "Parent node has no children")

    def test_parent_none_tag(self):
        try:
            leaf = LeafNode('b', "Bold Text")
            node = ParentNode(None, [leaf])
            node.to_html()
        except ValueError as e:
            self.assertEqual(f'{e}', "Parent node has no tag")

    def test_text_to_html(self):
        node = TextNode("This is a text node", TextType.PLAIN_TEXT)
        html_node = p_text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_code_to_html(self):
        node = TextNode("This is a code node", TextType.CODE_TEXT)
        html_node = p_text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code node")

    def test_text_to_html_link(self):
        node = TextNode("link text", TextType.LINK_ANCHOR_TEXT_URL, "www.lube.gov")
        html_node = p_text_node_to_html_node(node)
        self.assertEqual(html_node.tag, 'a')
        self.assertEqual(html_node.value, "link text")
        self.assertEqual(html_node.props["href"], "www.lube.gov")
        self.assertEqual(html_node.to_html(), '<a href="www.lube.gov">link text</a>')

    def test_text_to_html_img(self):
        node = TextNode("alt text here", TextType.IMAGE_ALT_TEXT_URL, "path/to/pic.gif")
        html_node = p_text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, '')
        self.assertEqual(html_node.props["src"], "path/to/pic.gif")
        self.assertEqual(html_node.props["alt"], "alt text here")
        self.assertEqual(html_node.to_html(), '<img src="path/to/pic.gif" alt="alt text here"></img>')

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = md_to_html(md)
        html = node.to_html()
        self.assertEqual(
            repr(html),
            repr("<div><p>This is <b>bolded</b> paragraph\ntext in a p\ntag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>"),
        )
    def test_codeblock(self):
        md = """
```c
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = md_to_html(md)
        html = node.to_html()
        self.assertEqual(
            repr(html),
            repr("<div><pre><code>c\nThis is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>"),
        )


if __name__ == "__main__":
    unittest.main()
