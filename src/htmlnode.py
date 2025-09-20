import re
from textnode import BlockType

class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        output_string = ""
        if self.props:
            for prop in self.props:
                output_string += f' {prop}="{self.props[prop]}"'
        return output_string

    def __repr__(self):
        output = f'\n.---HTMLNode---.\n'
        output += f'|  Tag:      {self.tag}\n'
        output += f'|  Value:    {self.value}\n'

        if self.children is not None:
            output += f'|  Children: {len(self.children)}\n'
            for i in range(len(self.children)):
                output += f'|       #{i+1}\n'
                output += f'|       tag: {self.children[i].tag}\n'
                output += f'|       val: {self.children[i].value}\n'
        else: output += f'|    *no children*\n'

        if self.props is not None:
            for prop in self.props:
                output += f'|  Props:    {len(self.props)}\n'
                for prop in self.props:
                    output += f'|       {prop}: {self.props[prop]}\n'
        else: output += f'|  *no props*   \n'
        output += f'`--------------`\n'
        return output

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props) 
        # None corresponds to where  ^^^^ "children" 
        # would be expected. LeafNodes can't have children

    def to_html(self):
        if self.value is None:
            raise ValueError("Leaf node has no value")
        if self.tag is None:
            return self.value

        return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        if not isinstance(children, list):
            super().__init__(tag, None, [children], props) # Just to make sure children is list
        else:
            super().__init__(tag, None, children, props) 
        #                     ^^^^
        # Parent Nodes have no text content

    def to_html(self):
        if self.tag is None:
            raise ValueError("Parent node has no tag")
        if not self.children or self.children == []:
            raise ValueError("Parent node has no children")

        # Open Tag
        output = ""
        if self.tag == 'code':
            output = '<pre>'                                    
        output += f'<{self.tag}{self.props_to_html()}>'        

        # Header
        # Strip MD header formatting
        if self.tag in ("ul", "ol", "blockquote"):
            for child in self.children:
                child.value = replace_md_block_format(self.tag, child.value)
        else:
            self.children[0].value = replace_md_block_format(self.tag, self.children[0].value)

        for child_node in self.children:
            output += child_node.to_html()
        output += f'</{self.tag}>'                            
        if self.tag == 'code':
            output += '</pre>'                                    
        # Close Tag
        return output
    
def replace_md_block_format(tag, md_string):
    match tag:
        case 'p' | BlockType.PARAGRAPH:
            return md_string
        case "code" | BlockType.CODE:
            return md_string.strip("```")
        case "blockquote" | BlockType.QUOTE:
            return md_string[2:].replace("\n>", '\n')
        case "ul" | BlockType.UNORDERED_LIST:
            return md_string.lstrip("- ").replace("\n- ", '\n')
        case "ol" | BlockType.ORDERED_LIST:
            return re.sub(r"^\d+\.\s", '', md_string, flags=re.M)
        case _:
            if tag[0] == 'h' or tag == BlockType.HEADING:
                return md_string.lstrip("# ")
            return md_string

