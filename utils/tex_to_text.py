import os
import re
from pathlib import Path
from plasTeX.TeX import TeX
from plasTeX.DOM import Text


def clean_text_tex(text, remove_line_breaks=True, remove_commands=True, remove_math_symbols=True, remove_equations=True):
    # Remove line breaks
    if remove_line_breaks:
        text = text.replace("\n", " ")
    
    if remove_math_symbols:
        # This example assumes equations start with "$" and end with "$"
        # Adjust the pattern as needed for your specific use case
        text = re.sub(r"\$[^\$]*\$", "", text)

    if remove_equations: 
        text = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', text, flags=re.DOTALL)

    if remove_commands:
        # Remove commands like \section{Introduction}
        text = re.sub(r'\\[a-zA-Z]+(\{.*?\})?', '', text)

    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text)

    # Remove unwanted characters (e.g., hyphens, underscores)
    text = re.sub(r"[-_]", "", text)

    return text


def remove_comments(text):
    return re.sub(r'(?<!\\)%.*', '', text)


def remove_commands(text):
    return re.sub(r'\\[a-zA-Z]+(\{.*?\})?', '', text)


def read_and_preprocess_tex_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()

    text = remove_comments(text)
    return text


def extract_sections(tex_content):
    section_pattern = r'\\section\{(.+?)\}((?:.|\n)*?)(?=\\section|\Z)'
    sections = re.finditer(section_pattern, tex_content, re.MULTILINE)

    extracted_sections = []

    for section in sections:
        title = section.group(1)
        content = section.group(2)

        extracted_sections.append({
            'title': title,
            'content': clean_text_tex(content, remove_line_breaks=True, remove_commands=True, remove_math_symbols=True, remove_equations=True)
        })

    return extracted_sections


def tex_to_sections(tex_file_path, output_dir, extract_file='extract.txt'):
    document_text = read_and_preprocess_tex_file(tex_file_path)
    sections = extract_sections(document_text)
    text = ''
    section_titles = []
    for idx, section in enumerate(sections, start=1):
        file_path = os.path.join(output_dir, f'section_{idx}.txt')
        section_titles += [section['title']]
        with open(file_path, 'w') as f:
            f.write(section['title'])
            content = section['content']
            f.write(content)
        text += section['title']
        text += content

    # Write the whole text to a file so we can work on it later if we notice some errors
    extract_path = os.path.join(output_dir, extract_file)
    with open(extract_path, 'w') as f:
        f.write(text)
    return sections


###### use plasTeX for tex processing ######
# this doas not work at the moment! 

def parse_tex_file(file_path):
    file_path = Path(file_path).resolve()

    tex = TeX()
    tex.ownerDocument.config['files']['filename'] = file_path
    tex.ownerDocument.config['general']['copy-theme-extras'] = False
    tex.ownerDocument.config['general']['theme'] = 'plain'
    tex.parse()

    return tex


def extract_text_platex(node):
    if isinstance(node, Text):
        return str(node)
    
    text = ''
    for child in node.childNodes:
        text += extract_text_platex(child)
    
    return text


def extract_sections_platex(document, section_name):
    sections = document.getElementsByTagName(section_name)
    extracted_sections = []

    for section in sections:
        title = extract_text_platex(section.attributes['title'])
        content = extract_text_platex(section)

        extracted_sections.append({
            'title': title,
            'content': content
        })

    return extracted_sections



def tex_to_files_platex(tex_file_path, output_dir, section_name='section', extract_file='extract.txt'):
    '''Converts a tex file to a text file for each section and a text file with the whole text.
    Returns a list of section titles. 
    However, this does not work at the moment!'''

    document = parse_tex_file(tex_file_path)
    print(document)

    text = extract_text_platex(document)
    print("#############################################")
    print(text)

    sections = extract_sections(document.ownerDocument, section_name)
    print("#############################################")
    print(sections)

    text = ''
    section_titles = []
    for idx, section in enumerate(sections, start=1):
        file_path = os.path.join(output_dir, f'section_{idx}.txt')
        section_titles += [section['title']]
        with open(file_path, 'w') as f:
            f.write(section['title'])
            f.write(section['content'])
        text += section['title']
        text += section['content']

    # Write the whole text to a file so we can work on it later if we notice some errors
    extract_path = os.path.join(output_dir, 'extract.txt')
    with open(extract_path, 'w') as f:
        f.write(text)
    return section_titles