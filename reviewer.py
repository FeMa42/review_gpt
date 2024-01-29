import os
from utils.pdf_to_text import pdf_to_sections
from utils.summary_creator_gpt import create_summary_chatgpt
from utils.summary_creator_local import create_summary_huggingface
from utils.large_text_handler import split_text_file_by_keywords
from utils.tex_to_text import tex_to_sections
from utils.pdf_nougat import PDFNougat


if __name__ == "__main__":
    input_file = '/Users/damian/Library/Mobile Documents/com~apple~CloudDocs/Projects/review_gpt/texts/SOIL/SOILTDM.pdf'
    projekt_name = 'test'

    # Extract text from PDF or use already extracted text
    extract_method = 'txt'  # 'pdf', 'tex', 'txt'
    
    split_text = False  # if true we split the text into chunks based on keywords
    # Keywords to split the text into sections for pdf review, summary 
    keywords = ['Introduction', 'Methods', 'Results', 'Discussion', 'Conclusion', 'Acknowledgements', 'References']

    # Model to use for review or summary
    use_chatgpt = False  # if true we use chatgpt, if false we use huggingface
    if use_chatgpt:
        model = 'gpt-4-turbo-preview'  # use chatgpt for review
    else:
        # model for CUDA GPUs with PyTorch: "NeuralBeagle14-7B" (I did not test this model yet)
        # model for Metal GPUs with MLX: "NeuralBeagle14-7B-mlx" (I tested this model and it works)
        model = "NeuralBeagle14-7B-mlx"  # 'NeuralBeagle14-7B-mlx', 'NeuralBeagle14-7B'
    is_summary = False  # if false we review the text, if true we create a summary

    # Create working directory
    working_dir = os.path.join("./texts/", projekt_name)
    if not os.path.isdir(working_dir):
        os.mkdir(working_dir)

    section_titles = []
    extract_path = os.path.join(working_dir, 'extract.txt')
    if extract_method == 'pdf':
        # Extract text from PDF using PyPDF2
        print("Extracting text from PDF file")
        # Split large text into chunks based on keywords
        sections = pdf_to_sections(input_file, working_dir, keywords, split_text=split_text)
        print("Extracted text from PDF file")
    elif extract_method == 'nougat':
        # Extract text from PDF using Nougat
        print("Extracting text from PDF file")
        pdf_nougat = PDFNougat()
        sections = pdf_nougat.extract_text_from_pdf(input_file, working_dir)
        print("Extracted text from PDF file")
    elif extract_method == 'tex':
        # Extract text from tex file. 
        # This can work better than the pdf extraction, because there might be less formatting issues. 
        print("Extracting text from tex file")
        sections = tex_to_sections(
             input_file, working_dir, extract_file='extract.txt', split_text=split_text)
        print("Extracted text from tex file")
    elif extract_method == 'txt-split':
        # Work with already split text files. 
        section_files = []
        i = 1
        while True:
            try:
                filename = f'section_{i}.txt'
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
    else: 
        if split_text:
            print("Reading text from file")
            with open(extract_path, 'r') as f:
                text = f.read()
            sections = split_text_file_by_keywords(
                text, working_dir, keywords,
                clean_extracted_chunk=True,
                add_spaces_to_chunk=False)  
            print("Extracted text from text file and splitted into chunks")
        else:
            print("Reading text from file")
            with open(extract_path, 'r') as f:
                text = f.read()
            sections = []
            sections.append({
                'title': projekt_name,
                'content': text
            })
            print("Extracted text from text file without splitting into chunks")

    # Create review or summary 
    if is_summary:
        method = 'summary'
    else:
        method = 'review'
    combined_summary_path = os.path.join(working_dir, f'{method} using {model}.txt')
    with open(combined_summary_path, 'w', encoding='utf-8') as output_file:
        for section in sections:
            content = section['content']
            title = section['title']
            print(f"Start {method} of {title} using {model} ...")
            if use_chatgpt:
                summary_part, finish_reason = create_summary_chatgpt(
                    content, section=f"{title} section" , model=model, is_summary=is_summary)
                print(f"Finished {method} of {title} using {model} because {finish_reason}")
            else:
                summary_part = create_summary_huggingface(
                    content, model=model, is_summary=is_summary)
                # print(f"Finished {method} of {title} using {model}")
                print(f"Finished review of {title} using {model}")
            output_file.write(f' {method} of {title}\n')
            output_file.write(summary_part)
            output_file.write('\n')
