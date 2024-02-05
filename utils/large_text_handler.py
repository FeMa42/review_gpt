import os
from utils.pdf_cleaner import clean_text, add_spaces, remove_line_breaks

def split_text_file(file_path, chunk_size=1000):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    words = text.split()
    num_chunks = len(words) // chunk_size + \
        (1 if len(words) % chunk_size else 0)

    for i in range(num_chunks):
        start = i * chunk_size
        end = (i + 1) * chunk_size
        chunk = " ".join(words[start:end])

        with open(f'chunk_{i+1}.txt', 'w', encoding='utf-8') as output_file:
            output_file.write(chunk)


def split_markdown_file(text, split_text, projekt_name, seperator='#'):
    if split_text:
        chunks = text.split(seperator)
        chunks = [chunk.strip() for chunk in chunks]
        chunks = [chunk for chunk in chunks if chunk]
        sections = []
        for chunk in chunks:
            title = chunk.split('\n')[0]
            if len(title) > 100:
                title = title[:100]
            sections.append({
                'title': title,
                'content': chunk
            })
    else: 
        sections = []
        sections.append({
            'title': projekt_name,
            'content': text
        })
    return sections
   

def split_text_file_by_keywords(text, working_dir, keywords, clean_extracted_chunk, add_spaces_to_chunk):

    # Convert the text and keywords to lowercase for case-insensitive matching
    text_lower = text.lower()
    text_lower = remove_line_breaks(text_lower)
    keywords_lower = [keyword.lower() for keyword in keywords]

    # Create a list of indices for each keyword
    indices = [0]
    section_titles = []
    section_titles.append('Title')
    for keyword in keywords_lower:
        index = text_lower.find(keyword)
        if index != -1:
            indices.append(index)
            section_titles += [keyword]

    indices.append(len(text))
    extracted_sections = []
    for i in range(len(indices) - 1):
        start = indices[i]
        end = indices[i + 1]

        chunk = text[start:end]

        if clean_extracted_chunk:
            print(f"Cleaning extracted chunk {i+1}")
            chunk = clean_text(chunk, remove_line_breaks=False,
                            remove_refernces=False, remove_math_symbols=True)
        if add_spaces_to_chunk:
            print(f"Adding spaces to chunk {i+1}")
            chunk = add_spaces(chunk)

        extracted_sections.append({
            'title': section_titles[i],
            'content': chunk
        })
        
        filename = f'section_{i+1}.txt'
        file_path = os.path.join(working_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(chunk)
    return extracted_sections



