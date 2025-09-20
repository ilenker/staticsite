import re
from textnode import TextNode, TextType, BlockType
from htmlnode import *

class UnbalancedDelimiters(Exception):
    pass

def p_text_node_to_html_node(text_node):
    if not isinstance(text_node, TextNode):
        raise ValueError("p_text_node_to_html_node expects TextNode object")

    match text_node.text_type:
        case TextType.PLAIN_TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD_TEXT:
            return LeafNode('b', text_node.text)
        case TextType.ITALIC_TEXT:
            return LeafNode('i', text_node.text)
        case TextType.CODE_TEXT:
            return LeafNode("code", text_node.text)
        case TextType.LINK_ANCHOR_TEXT_URL:
            return LeafNode('a', text_node.text, {"href": text_node.url})
        case TextType.IMAGE_ALT_TEXT_URL:
            return LeafNode("img", '', {"src": text_node.url, "alt": text_node.text})
        case _:
            raise TypeError("Invalid text type")

def p_split_text_nodes(old_nodes, delimiter, text_type):
    if delimiter == '':
        return old_nodes
    new_nodes = []
    for node in old_nodes:                       
        split_at_delim = node.text.split(delimiter)

        if len(split_at_delim) % 2 == 0:
            raise UnbalancedDelimiters(f'Error: "{node.text}" has unbalanced delimiters')

        while len(split_at_delim) > 0:
            if split_at_delim[0] == '': # Case 1: starts with code
                if len(split_at_delim) > 1:
                    new_nodes.append(TextNode(''.join(split_at_delim[:2]), text_type)) # + '!CODE!')
                    del split_at_delim[:2]
                else:
                    return new_nodes
            else:   
                # First is not code, other text
                new_nodes.append(TextNode(''.join(split_at_delim[:1]), node.text_type))  # + '!TEXT!')
                del split_at_delim[:1]
                if len(split_at_delim) > 0:
                    new_nodes.append(TextNode(''.join(split_at_delim[:1]), text_type)) # + '!CODE!')
                    del split_at_delim[:1]
    return new_nodes

def p_extract_md_images(md_string):
    return re.findall(r'!\[(.*?)\]\((.*?)\)', md_string)

def p_extract_md_links(md_string):
    return re.findall(r'(?<!\!)\[(.*?)\]\((.*?)\)', md_string)

def p_split_image_nodes(old_nodes):
    # TODO: Validate input
    new_nodes = []

    for node in old_nodes:
        if node.text_type == TextType.PLAIN_TEXT:
            input = node.text
            img_extract = p_extract_md_images(input)
            if not img_extract: 
                new_nodes.append(node)
                continue

            next = input.split(f'![{img_extract[0][0]}]({img_extract[0][1]})', 1)
            if len(next) > 0: # Check for splits
                for i in range(0, len(img_extract)):
                    if i != 0:
                        next = next.split(f'![{img_extract[i][0]}]({img_extract[i][1]})', 1)
                    if next[0] != '':
                        new_nodes.append(TextNode(next[0], TextType.PLAIN_TEXT))
                    new_nodes.append(TextNode(img_extract[i][0], TextType.IMAGE_ALT_TEXT_URL, img_extract[i][1]))
                    if len(next) > 1: 
                        next = next[1] 

                if next != '':
                    new_nodes.append(TextNode(next, TextType.PLAIN_TEXT))
        else:
            new_nodes.append(node)
    return new_nodes
 
def p_split_link_nodes(old_nodes):
    # TODO: Validate input
    new_nodes = []

    for node in old_nodes:
        if node.text_type == TextType.PLAIN_TEXT:
            input = node.text
            link_extract = p_extract_md_links(input)
            if not link_extract: 
                new_nodes.append(node)
                continue

            next = re.split(fr'(?<!\!)\[{link_extract[0][0]}\]\({link_extract[0][1]}\)', input, maxsplit=1)
            if len(next) > 0: # Check for splits
                for i in range(0, len(link_extract)):
                    if i != 0:
                        next = re.split(fr'(?<!\!)\[{link_extract[i][0]}\]\({link_extract[i][1]}\)', next, maxsplit=1) 
                    if next[0] != '':
                        new_nodes.append(TextNode(next[0], TextType.PLAIN_TEXT))
                    new_nodes.append(TextNode(link_extract[i][0], TextType.LINK_ANCHOR_TEXT_URL, link_extract[i][1]))
                    if len(next) > 1: 
                        next = next[1] 

                if next != '':
                    new_nodes.append(TextNode(next, TextType.PLAIN_TEXT))
        else:
            new_nodes.append(node)
    return new_nodes

def p_text_to_text_nodes(text):
    raw_text_node = [TextNode(text, TextType.PLAIN_TEXT)]
    nodes = p_split_text_nodes(raw_text_node, "**", TextType.BOLD_TEXT)
    nodes = p_split_text_nodes(nodes, "_", TextType.ITALIC_TEXT)
    nodes = p_split_text_nodes(nodes, "`", TextType.CODE_TEXT)
    nodes = p_split_image_nodes(nodes)
    nodes = p_split_link_nodes(nodes)
    return nodes

def p_markdown_to_blocks(text):
    if not isinstance(text, str):
        raise TypeError
    blocks = re.split(r'\n+\n', text)
    blocks = [block.strip() for block in blocks]
    blocks = list(filter(lambda x: x!='', blocks))
    return blocks 

def p_block_to_blocktype(block):
    if not isinstance(block, str):
        raise TypeError
    if block == '':
        return BlockType.PARAGRAPH

    # Headers
    if re.match(r'^#{1,6} ', block) is not None:  
        heading_num = len(re.match(r'^#{1,6} ', block).group()) - 1
        return (BlockType.HEADING, heading_num)

    # Code Block
    if re.match(r'^(`{3})(.*)(`{3})$', block, re.DOTALL): 
        return BlockType.CODE

    # Quote Block
    if block.startswith('>'):
        temp = block 
        temp = temp.split('\n')
        flag = True 
        for line in temp:
            if not line.startswith('>'):
                flag = False
        if flag:
            return BlockType.QUOTE 

    # Unordered List
    if re.match(r'^(?:- .*\n?)*$', block, re.MULTILINE):
        return BlockType.UNORDERED_LIST
    
    # Ordered List
    if block.startswith("1. "):
        temp = block
        n = 2
        flag = True
        while temp.find('\n') != -1:
            temp = temp[temp.find('\n') + 1:]
            if temp.startswith(f"{n}. "):
                n += 1
            else:
                flag = False
                break
        if flag:
            return BlockType.ORDERED_LIST 

    # Default Case
    return BlockType.PARAGRAPH
    

