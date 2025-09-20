import os, shutil
from textnode import *
from htmlnode import *
from parsing import *
from conversion import md_to_html

pjoin = os.path.join
pexists = os.path.exists
pisdir = os.path.isdir
CWD = os.getcwd()

def main():
    #print((root.to_html()).replace('\n', '<br>'))
    clean_path("public")
    populate_directory("static", "public")
    content_directories_md = [
            "index",
            "blog/glorfindel/index",
            "blog/tom/index",
            "blog/contact/index",
            "blog/majesty/index",
            "index",
    ]
    generate_page_r("content", "template.html", "public")
    
def clean_path(dest_path):
    shutil.rmtree(pjoin(CWD, dest_path))
    os.mkdir(pjoin(CWD, dest_path))
 
def populate_directory(src_path, dest_path):
    src_path_full = pjoin(CWD, src_path)                
    if not pexists(src_path_full):
        raise FileNotFoundError(f'{src_path_full} not found.')
    if not os.path.exists(pjoin(CWD, dest_path)):  
        raise FileNotFoundError(f'{dest_path} not found.')
    
    for path in os.listdir(src_path_full):
        if pisdir(pjoin(src_path_full, path)):
            os.mkdir(pjoin(CWD, f"{dest_path}/{path}"))
            populate_directory(pjoin(src_path_full, path), pjoin(dest_path, path))
            continue
        shutil.copy(pjoin(src_path_full, path),
                    pjoin(os.getcwd(), dest_path))

def extract_title(md):
    if not isinstance(md, str):
        raise TypeError
    if md.startswith("# "):
        eol = md.find('\n') if md.find('\n') != -1 else len(md)
        return md[2:eol]

    sol = 3 + md.find("\n# ") if md.find("\n# ") != -1 else None
    if sol:
        eol = md[sol:].find('\n') if md[sol:].find('\n') != -1 else len(md)
        return md[sol:eol]
    raise Exception("Error: '# ' not found in string")

def generate_page(from_path, template_path, dest_path):
    print(f'Generating page from "{from_path}" to "{dest_path}" using "{template_path}"')
    with open(pjoin(CWD, from_path), 'r', encoding='utf-8') as f:
        md_file = f.read()  
    with open(pjoin(CWD, template_path), 'r', encoding='utf-8') as f:
        template_file = f.read()

    html_content = md_to_html(md_file).to_html()
    try:
        title = extract_title(md_file)
    except Exception as e:
        print(e)
        title = "NO TITLE FOUND"
    template_file = template_file.replace(
        '{{ Title }}', title).replace(
        '{{ Content }}', html_content)

    full_dest_path = pjoin(CWD, dest_path)
    if not pexists(os.path.dirname(full_dest_path)):
        os.makedirs(os.path.dirname(full_dest_path))
    with open(full_dest_path, 'a', encoding='utf-8') as f:
        f.write(template_file)

def generate_page_r(src_path, template_path, dest_path):
    matches = []

    def find_md_files(inner_path):
        nonlocal matches
        for path in os.listdir(inner_path):
            if pisdir(pjoin(inner_path, path)):
                find_md_files(pjoin(inner_path, path))
                continue
            if path[-3:] == ".md":
                matches.append(f'{inner_path}/{path[:-3]}'.removeprefix(src_path+'/'))

    find_md_files(src_path) 

    for path in matches:
        generate_page(f'{src_path}/{path}.md', template_path, f'{dest_path}/{path}.html')


main()
