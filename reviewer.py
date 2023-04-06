import os
from utils.pdf_to_text import extract_pdf_text, pdf_to_sections
from utils.summary_creator_gpt import create_summary_chatgpt
from utils.large_text_handler import split_text_file_by_keywords
from utils.tex_to_text import tex_to_sections


if __name__ == "__main__":
    # input_file = './texts/SOIL/soiltdm.tex'
    # projekt_name = 'SOIL_TDM'
    input_file = '/Users/damian/soiltdm.pdf'
    projekt_name = 'SOIL_TDM_PDF'

    # Extract text from PDF
    extract_method = 'pdf'  # 'pdf', 'tex', 'txt-whole', 'txt-split'

    model = 'gpt-3.5-turbo'  # use chatgpt for review
    is_summary = False  # if false we review the text, if true we create a summary

    # Keywords to split the text into sections for pdf review, summary 
    keywords = ['Abstract', '1 Introduction', '2 Background',
                '3 Method', '4 Related Work', '5 Experiments', '6 Conclusion']

    # Create working directory
    working_dir = os.path.join("./texts/", projekt_name)
    if not os.path.isdir(working_dir):
        os.mkdir(working_dir)


    section_titles = []
    extract_path = os.path.join(working_dir, 'extract.txt')
    if extract_method == 'pdf':
        # Extract text from PDF
        print("Extracting text from PDF file")
        # Split large text into chunks based on keywords
        sections = pdf_to_sections(input_file, working_dir, keywords)
        print("Extracted text from PDF file")
    elif extract_method == 'tex':
        # Extract text from tex file. 
        # This can work better than the pdf extraction, because there might be less formatting issues. 
        print("Extracting text from tex file")
        sections = tex_to_sections(
             input_file, working_dir, extract_file='extract.txt')
        print("Extracted text from tex file")
    elif extract_method == 'txt-split':
        # Work with already split text files. 
        # This can be helpfull if you want to finetune the chunks by hand or if you want to use a different splitting method.
        section_files = []
        i = 1
        while True:
            try:
                filename = f'section_{i+1}.txt'
                file_path = os.path.join(working_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as input_file:
                    content = input_file.read()
                    section_files.append(content)
                    i += 1
            except FileNotFoundError:
                break
        # Now section_files is a list containing the content of each section file
        sections = []
        print("found " + str(len(section_files)) + " section files")
        if len(section_files) <= len(section_titles):
            print("found less than or equal amount of section files compared to keywords")
            use_section_titles = True
        else:
            print("found more section files than section titles")
            use_section_titles = False
        for idx, content in enumerate(section_files):
            if use_section_titles:
                title = section_titles[idx]
            else:
                title = f'section_{idx+1}.txt'
            content = content
            sections.append({
                'title': title,
                'content': content
            })
    else: # extract_method == 'txt-whole':
        # use whole text file, and split it into chunks based on keywords. If you modified the text file by hand, you can use this method. 
        # Please note that linebreaks are removed before the text is split into chunks. 
        print("Reading text from file")
        with open(extract_path, 'r') as f:
            text = f.read()
        # Split large text into chunks based on keywords
        sections = split_text_file_by_keywords(
            text, working_dir, keywords,
            clean_extracted_chunk=True,
            add_spaces_to_chunk=False)  # add_spaces_to_chunk adds spaces based on word frequency. Activate if there are errors in the text
        print("Extracted text from text file")

    if is_summary:
        method = 'summary'
    else:
        method = 'review'
    combined_summary_path = os.path.join(working_dir, f'{method} using {model} .txt')
    with open(combined_summary_path, 'w', encoding='utf-8') as output_file:
        for section in sections:
            content = section['content']
            title = section['title']
            print(f"Start {method} of {title} using {model} ...")
            summary_part, finish_reason = create_summary_chatgpt(
                content, section=f"{title} section" , model=model, is_summary=False)
            print(f"Finished {method} of {title} using {model} because {finish_reason}")
            output_file.write(f' {method} of {title}\n')
            output_file.write(summary_part)
            output_file.write('\n')
