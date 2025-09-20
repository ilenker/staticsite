from parsing import *
from textnode import *
from htmlnode import *

def md_to_html(md):
    if not isinstance(md, str):
        raise TypeError("o7 Input should be a string")

    blocks = p_markdown_to_blocks(md)
    html_parent_nodes = []
    for block in blocks:
        block_type = p_block_to_blocktype(block)

        if block_type == BlockType.CODE:
            code_block_content = p_text_node_to_html_node(TextNode(block, TextType.PLAIN_TEXT))
            parent_node = ParentNode(block_type_to_tag(block_type), code_block_content)
            html_parent_nodes.append(parent_node)
            continue

        if block_type in (BlockType.UNORDERED_LIST, BlockType.ORDERED_LIST):
            block = replace_md_block_format(block_type, block) 
            block = block.split('\n')
            for i in range(len(block)):
                block[i] = f'<li>{block[i]}</li>'
            block = '\n'.join(block)

        text_subnodes = p_text_to_text_nodes(block)
        html_subnodes = [p_text_node_to_html_node(node) for node in text_subnodes]
        #LeafNodes^^
        parent_node = ParentNode(block_type_to_tag(block_type), html_subnodes)
        html_parent_nodes.append(parent_node)

    root_node = ParentNode("div", html_parent_nodes)

    return root_node

def block_type_to_tag(block_type):
    match(block_type):
        case BlockType.PARAGRAPH:
            return 'p'
        case (BlockType.HEADING, _):
            return f'h{block_type[1]}'
        case BlockType.CODE:
            return "code"
        case BlockType.QUOTE:
            return "blockquote"
        case BlockType.UNORDERED_LIST:
            return "ul"
        case BlockType.ORDERED_LIST:
            return "ol"
    return ValueError(f"Unknown BlockType: {block_type}")
