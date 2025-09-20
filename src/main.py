import os, shutil, sys
from textnode import *
from htmlnode import *
from parsing import *
from conversion import md_to_html

pjoin = os.path.join
pexists = os.path.exists
pisdir = os.path.isdir

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else '/'
    create_paths() 
    clean_path(f"docs")
    populate_directory("static", "docs")
    generate_page_r(f"content",
                    f"template.html",
                    f"docs", basepath)
    
def clean_path(dest_path):
    if pexists(dest_path):
        shutil.rmtree(dest_path)
    os.mkdir(dest_path)
 
def populate_directory(src_path, dest_path):
    src_path_full = src_path                
    if not pexists(src_path_full):
        raise FileNotFoundError(f'{src_path_full} not found.')
    if not os.path.exists(dest_path):  
        raise FileNotFoundError(f'{dest_path} not found.')
    
    for path in os.listdir(src_path_full):
        if pisdir(pjoin(src_path_full, path)):
            os.mkdir(f"{dest_path}/{path}")
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

    sof = 3 + md.find("\n# ") if md.find("\n# ") != -1 else None
    if sof:
        eol = md[sof:].find('\n') if md[sof:].find('\n') != -1 else len(md)
        return md[sof:eol]
    raise Exception("Error: '# ' not found in string")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f'Generating page from "{from_path}" to "{dest_path}" using "{template_path}"')
    with open(from_path, 'r', encoding='utf-8') as f:
        md_file = f.read()  
    with open(template_path, 'r', encoding='utf-8') as f:
        template_file = f.read()

    html_content = md_to_html(md_file).to_html()
    try:
        title = extract_title(md_file)
    except Exception as e:
        print(e)
        title = "NO TITLE FOUND"
    template_file = template_file.replace('{{ Title }}', title
                                ).replace('{{ Content }}', html_content)
    template_file = template_file.replace('href="/', f'href="{basepath}'
                                ).replace('src="/', f'src="{basepath}')

    full_dest_path = dest_path
    if not pexists(os.path.dirname(full_dest_path)):
        os.makedirs(os.path.dirname(full_dest_path))
    with open(full_dest_path, 'a', encoding='utf-8') as f:
        f.write(template_file)

def generate_page_r(src_path, template_path, dest_path, basepath):
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
        generate_page(f'{src_path}/{path}.md', template_path, f'{dest_path}/{path}.html', basepath)

def create_paths():
    paths = [
        "static",
        "content",
        "docs",
    ]
    for path in paths:
        if not pexists(path):
            os.mkdir(path)
    return 0

main()
