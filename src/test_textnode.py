import unittest

from textnode import TextNode, TextType 
from htmlnode import HTMLNode, LeafNode, ParentNode
from parsing import *

class TestTextNode(unittest.TestCase):

    def test_eq(self):
        node  = TextNode("This is a text node", TextType.BOLD_TEXT)
        node2 = TextNode("This is a text node", TextType.BOLD_TEXT)
        self.assertEqual(node, node2)

    def test_text_not_eq(self):
        node  = TextNode("This is a text node", TextType.BOLD_TEXT)
        node2 = TextNode("This is a text nodee", TextType.BOLD_TEXT)
        self.assertNotEqual(node, node2)

    def test_type_not_eq(self):
        node  = TextNode("This is a text node", TextType.BOLD_TEXT)
        node2 = TextNode("This is a text node", TextType.ITALIC_TEXT)
        self.assertNotEqual(node, node2)

    def test_url_match(self):
        node  = TextNode("This is a link node", TextType.LINK_ANCHOR_TEXT_URL, "test")
        node2 = TextNode("This is a link node", TextType.LINK_ANCHOR_TEXT_URL, "test")
        self.assertEqual(node, node2)

    def test_url_match_empty(self):
        node  = TextNode("This is a link node", TextType.LINK_ANCHOR_TEXT_URL)
        node2 = TextNode("This is a link node", TextType.LINK_ANCHOR_TEXT_URL)
        self.assertEqual(node, node2)

    def test_parser_plain(self):
        unparsed_nodes = [TextNode("Text has no bold", TextType.PLAIN_TEXT)]
        parsed_nodes = p_split_text_nodes(unparsed_nodes, '', TextType.PLAIN_TEXT)

        self.assertEqual(parsed_nodes[0].text, "Text has no bold")
        self.assertEqual(parsed_nodes[0].text_type, TextType.PLAIN_TEXT)

    def test_parser_bold(self):
        unparsed_nodes = [TextNode("Text has **bold text inside**", TextType.PLAIN_TEXT)]
        parsed_nodes = p_split_text_nodes(unparsed_nodes, '**', TextType.BOLD_TEXT)

        self.assertEqual(parsed_nodes[0].text, "Text has ")
        self.assertEqual(parsed_nodes[0].text_type, TextType.PLAIN_TEXT)

        self.assertEqual(parsed_nodes[1].text, "bold text inside")
        self.assertEqual(parsed_nodes[1].text_type, TextType.BOLD_TEXT)
    
    def test_parser_bold_italic_code(self):
        unparsed_nodes = [TextNode("This is a long **unparsed text node**. We will _parse it_ with some `well written code` yes", TextType.PLAIN_TEXT)]

        parsed_nodes = p_split_text_nodes(unparsed_nodes, '**', TextType.BOLD_TEXT)
        parsed_nodes = p_split_text_nodes(parsed_nodes, '_', TextType.ITALIC_TEXT)
        parsed_nodes = p_split_text_nodes(parsed_nodes, '`', TextType.CODE_TEXT)

        self.assertEqual(parsed_nodes[0].text, "This is a long ")
        self.assertEqual(parsed_nodes[0].text_type, TextType.PLAIN_TEXT)

        self.assertEqual(parsed_nodes[1].text, "unparsed text node")
        self.assertEqual(parsed_nodes[1].text_type, TextType.BOLD_TEXT)

        self.assertEqual(parsed_nodes[2].text, ". We will ")
        self.assertEqual(parsed_nodes[2].text_type, TextType.PLAIN_TEXT)

        self.assertEqual(parsed_nodes[3].text, "parse it")
        self.assertEqual(parsed_nodes[3].text_type, TextType.ITALIC_TEXT)

        self.assertEqual(parsed_nodes[4].text, " with some ")
        self.assertEqual(parsed_nodes[4].text_type, TextType.PLAIN_TEXT)

        self.assertEqual(parsed_nodes[5].text, "well written code")
        self.assertEqual(parsed_nodes[5].text_type, TextType.CODE_TEXT)

        self.assertEqual(parsed_nodes[6].text, " yes")
        self.assertEqual(parsed_nodes[6].text_type, TextType.PLAIN_TEXT)

    def test_parser_empty_node(self):
        unparsed_nodes = [TextNode('', TextType.PLAIN_TEXT)]
        parsed_nodes = p_split_text_nodes(unparsed_nodes, '**', TextType.BOLD_TEXT)
        self.assertEqual(len(parsed_nodes), 0)

    def test_parser_unbalanced_delims_easy(self):
        raised = 0
        unparsed_nodes = [TextNode('Text **', TextType.PLAIN_TEXT)]
        try:
            parsed_nodes = p_split_text_nodes(unparsed_nodes, '**', TextType.BOLD_TEXT)
        except UnbalancedDelimiters as e:
            self.assertEqual(raised, 0, f'{e}')
            raised = 1
        self.assertEqual(1, raised, "UnbalancedDelimiters was not raised")

    def test_parser_unbalanced_delims_hard(self):
        raised = 0
        unparsed_nodes = [TextNode('Text **Bold**, but then **half bold', TextType.PLAIN_TEXT)]
        try:
            parsed_nodes = p_split_text_nodes(unparsed_nodes, '**', TextType.BOLD_TEXT)
        except UnbalancedDelimiters as e:
            self.assertEqual(raised, 0, f'{e}')
            raised = 1
        self.assertEqual(1, raised, f'UnbalancedDelimiters was not raised on "{unparsed_nodes[0].text}"')

    def test_parser_unbalanced_delims_final_boss(self):
        raised = 0
        unparsed_nodes = [TextNode('Text **Bold**, but then `half code and _half italic', TextType.PLAIN_TEXT)]
        try:
            parsed_nodes = p_split_text_nodes(unparsed_nodes, '**', TextType.BOLD_TEXT)
            parsed_nodes = p_split_text_nodes(parsed_nodes, '`', TextType.CODE_TEXT)
            parsed_nodes = p_split_text_nodes(parsed_nodes, '_', TextType.ITALIC_TEXT)
        except UnbalancedDelimiters as e:
            self.assertEqual(raised, 0, f'{e}')
            raised = 1

    def test_parser_unbalanced_delims_nested(self):
        raised = 0
        unparsed_nodes = [TextNode('`Test **nested text** please be fine`', TextType.PLAIN_TEXT)]
        try:
            parsed_nodes = p_split_text_nodes(unparsed_nodes, '**', TextType.BOLD_TEXT)
            parsed_nodes = p_split_text_nodes(parsed_nodes, '`', TextType.CODE_TEXT)
        except UnbalancedDelimiters as e:
            self.assertEqual(raised, 0, f'{e}')
            raised = 1
        self.assertEqual(1, raised, f'UnbalancedDelimiters was not raised on "{unparsed_nodes[0].text}"')       

    def test_extract_md_images(self):
        matches = p_extract_md_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_md_links(self):
        matches = p_extract_md_links(
            "This is text with an [link](https://i.imgur.com)"
        )
        self.assertListEqual([("link", "https://i.imgur.com")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN_TEXT,
        )
        new_nodes = p_split_image_nodes([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN_TEXT),
                TextNode("image", TextType.IMAGE_ALT_TEXT_URL, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PLAIN_TEXT),
                TextNode(
                    "second image", TextType.IMAGE_ALT_TEXT_URL, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link yes](https://i.imgur.gov) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN_TEXT,
        )
        new_nodes = p_split_link_nodes([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.PLAIN_TEXT),
                TextNode("link yes", TextType.LINK_ANCHOR_TEXT_URL, "https://i.imgur.gov"),
                TextNode(" and another ![second image](https://i.imgur.com/3elNhQu.png)", TextType.PLAIN_TEXT),
            ],
            new_nodes,
        )

    def test_text_to_nodes(self):
        raw_text = 'This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)'
        nodes = p_text_to_text_nodes(raw_text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.PLAIN_TEXT),
                TextNode("text", TextType.BOLD_TEXT),
                TextNode(" with an ", TextType.PLAIN_TEXT),
                TextNode("italic", TextType.ITALIC_TEXT),
                TextNode(" word and a ", TextType.PLAIN_TEXT),
                TextNode("code block", TextType.CODE_TEXT),
                TextNode(" and an ", TextType.PLAIN_TEXT),
                TextNode("obi wan image", TextType.IMAGE_ALT_TEXT_URL, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.PLAIN_TEXT),
                TextNode("link", TextType.LINK_ANCHOR_TEXT_URL, "https://boot.dev"),
            ],
            nodes
        )

    def test_text_to_nodes_variation(self):
        raw_text = '**This is** text with an italic _word_ and a `code block` and an [obi wan link](https://i.imgur.com) and an ![image png](https://boot.dev/img.png)'
        nodes = p_text_to_text_nodes(raw_text)
        self.assertListEqual(
            [
                TextNode("This is", TextType.BOLD_TEXT),
                TextNode(" text with an italic ", TextType.PLAIN_TEXT),
                TextNode("word", TextType.ITALIC_TEXT),
                TextNode(" and a ", TextType.PLAIN_TEXT),
                TextNode("code block", TextType.CODE_TEXT),
                TextNode(" and an ", TextType.PLAIN_TEXT),
                TextNode("obi wan link", TextType.LINK_ANCHOR_TEXT_URL, "https://i.imgur.com"),
                TextNode(" and an ", TextType.PLAIN_TEXT),
                TextNode("image png", TextType.IMAGE_ALT_TEXT_URL, "https://boot.dev/img.png"),
            ],
            nodes
        )

    def test_text_to_nodes_variation_two(self):
        raw_text = '![img](img.url) ![img2](img.url2) []()[]() these are *empty*![]'
        nodes = p_text_to_text_nodes(raw_text)
        self.assertListEqual(
            [
                TextNode("img", TextType.IMAGE_ALT_TEXT_URL, "img.url"),
                TextNode(" ", TextType.PLAIN_TEXT),
                TextNode("img2", TextType.IMAGE_ALT_TEXT_URL, "img.url2"),
                TextNode(" ", TextType.PLAIN_TEXT),
                TextNode("", TextType.LINK_ANCHOR_TEXT_URL, ""),
                TextNode("", TextType.LINK_ANCHOR_TEXT_URL, ""),
                TextNode(" these are *empty*![]", TextType.PLAIN_TEXT),
            ],
            nodes
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = p_markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
    )

    def test_markdown_to_blocks_excess_blocks(self):
        md = """
This is **bolded** paragraph



This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line





- This is a list
- with items

"""
        blocks = p_markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
    )

    def test_block_parsing_isolated(self):
        blocks = [
            "# Header",
            "### Header",
            "###### Header",
            "```code```",
            "``````",
            ">quote",
            ">to be or not to be,\n>that is the question",
            "- item",
            "- apple\n- peach",
            "1. 1st",
            "1. 1st\n2. 2nd",

            "Para",
            "#Para",
            "####### Para",
            " # Para",
            " ```Para```",
            "2. Para",
            " 1. Para",
            "1. Para\n3. ",
            " >Para",
            " - Para",
            "-Para",
        ]
        processed = []
        for block in blocks:
            processed.append(p_block_to_blocktype(block))

        self.assertListEqual(processed, [
            (BlockType.HEADING, 1),
            (BlockType.HEADING, 3),
            (BlockType.HEADING, 6),
            BlockType.CODE,
            BlockType.CODE,
            BlockType.QUOTE,
            BlockType.QUOTE,
            BlockType.UNORDERED_LIST,
            BlockType.UNORDERED_LIST,
            BlockType.ORDERED_LIST,
            BlockType.ORDERED_LIST,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
            BlockType.PARAGRAPH,
        ])


    def test_block_parsing_context_simple(self):
        text = """# Here We Go, Mang: The story of Golang

### **Contents**

1. Chapter One
2. Chapter Two

Paragraph yes `code` in **bold**.

## Subheading

```big ol block of code```

>to be or nah
>that is questionable

#### On the agenda, in no particular order:

- Say goodbye
- Start by saying hello
- Change your mind last minute
- Cancel meeting"""

        blocks = p_markdown_to_blocks(text)
        processed_blocks = []

        for block in blocks:
            processed_blocks.append(p_block_to_blocktype(block))

        self.assertListEqual(processed_blocks, [
            (BlockType.HEADING, 1),
            (BlockType.HEADING, 3),
            BlockType.ORDERED_LIST,
            BlockType.PARAGRAPH,
            (BlockType.HEADING, 2),
            BlockType.CODE,
            BlockType.QUOTE,
            (BlockType.HEADING, 4),
            BlockType.UNORDERED_LIST,
        ])

    def test_block_parsing_context_excess_newlines(self):
        text = """
# Here We Go, Mang: The story of Golang



### **Contents**

1. Chapter One
2. Chapter Two

Paragraph yes `code` in **bold**.

## Subheading

```big ol block of code```


>to be or nah
>that is questionable


#### On the agenda, in no particular order:


- Say goodbye
- Start by saying hello
- Change your mind last minute
- Cancel meeting


"""

        blocks = p_markdown_to_blocks(text)
        processed_blocks = []
        print("********************************")
        for block in blocks:
            processed_blocks.append(p_block_to_blocktype(block))
            print(f"  --------{p_block_to_blocktype(block)}--------")
            print(block)
        print("********************************")

        self.assertListEqual(processed_blocks, [
            (BlockType.HEADING, 1),
            (BlockType.HEADING, 3),
            BlockType.ORDERED_LIST,
            BlockType.PARAGRAPH,
            (BlockType.HEADING, 2),
            BlockType.CODE,
            BlockType.QUOTE,
            (BlockType.HEADING, 4),
            BlockType.UNORDERED_LIST,
        ])

if __name__ == "__main__":
    unittest.main()
