import os
from utils.pdf_to_text import pdf_to_sections
from utils.llm_interface import interface_chatgpt, interface_huggingface
from utils.prompt_generator import generate_prompt
from utils.large_text_handler import split_text_file_by_keywords, split_markdown_file
from utils.tex_to_text import tex_to_sections
from utils.pdf_nougat import PDFNougat


if __name__ == "__main__":
    input_file = '/Users/damian/Library/Mobile Documents/com~apple~CloudDocs/Projects/review_gpt/texts/SOIL/SOILTDM.pdf'
    projekt_name = 'soiltdm'

    # Extract text from PDF or use already extracted text
    # If you have a pdf I recommend 'nougat'; the alternative is 'pdf', 
    # if the text is already extracted use 'txt', 
    # if you have a tex file you can use 'tex'
    extract_method = 'nougat' # 'nougat', 'pdf', 'txt', 'tex'
    
    # Split text into sections based on keywords or markdown headers
    split_text = 'markdown'  # 'keywords', 'markdown', None
    keywords = ['Introduction', 'Methods', 'Results', 'Discussion',
                'Conclusion', 'Acknowledgements', 'References']
    md_seperator = '#' # typical markdown header -> e.g. # Introduction
    if split_text == 'markdown':
        use_md_split = True
    else:
        use_md_split = False

    # Using a LLModel for review or summary
    do_llm_processing = True  # if true we use the language model, if false we only extract the text
    use_chatgpt = True  # if true we use chatgpt, if false we use a huggingface model
    if use_chatgpt:
        model = 'gpt-4-turbo-preview'  # use chatgpt for review
    else:
        # model for CUDA GPUs with PyTorch: "NeuralBeagle14-7B" (I did not test this model yet)
        # model for Metal GPUs with MLX: "NeuralBeagle14-7B-mlx" (I tested this model and it works)
        model = "NeuralBeagle14-7B-mlx"  # 'NeuralBeagle14-7B-mlx', 'NeuralBeagle14-7B'
    is_summary = False  # if false we review the text, if true we create a summary

    # Prompt generation and compression
    # if you compress the prompt think about activating the the text splitting (using markdown headers if you extracted the pdf using nougat)
    # if compress_prompt is false we use the full text as prompt for the language model
    compress_prompt = True
    max_compressed_tokens = 8000  # maximum tokens for the compressed prompt

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
        sections = pdf_to_sections(input_file, working_dir, keywords, split_text=False)
        print("Extracted text from PDF file")
    elif extract_method == 'nougat':
        # Extract text from PDF using Nougat
        print("Extracting text from PDF file")
        pdf_nougat = PDFNougat()
        sections = pdf_nougat.extract_text_from_pdf(
            input_file, working_dir, use_split=use_md_split, projekt_name=projekt_name, md_seperator=md_seperator)
        print("Extracted text from PDF file")
    elif extract_method == 'tex':
        # Extract text from tex file. 
        # This can work better than the pdf extraction, because there might be less formatting issues. 
        print("Extracting text from tex file")
        sections = tex_to_sections(
             input_file, working_dir, extract_file='extract.txt', split_text=True)
        print("Extracted text from tex file")
    else: # extract_method == 'txt'
        print("Reading text from file")
        with open(extract_path, 'r') as f:
            text = f.read()
        if split_text == 'keywords':
            sections = split_text_file_by_keywords(
                text, working_dir, keywords,
                clean_extracted_chunk=True,
                add_spaces_to_chunk=False)  
            print("Extracted text from text file and splitted into chunks")
        else:
            sections = split_markdown_file(
                text, split_text=use_md_split, projekt_name=projekt_name, seperator=md_seperator)
            print("Extracted text from text file and splitted into chunks")

    # Create review or summary 
    if is_summary:
        method = 'summary'
    else:
        method = 'review'
    combined_summary_path = os.path.join(working_dir, f'{method} using {model}.txt')
    with open(combined_summary_path, 'w', encoding='utf-8') as output_file:
        input_text = []
        for section in sections:
            input_text.append(section['content'])
        # Generate compressed prompt for review or summary
        print(f"Start prompt generation for {method} ...")
        prompt = generate_prompt(input_text, compress_prompt=compress_prompt,
                                 max_tokens=max_compressed_tokens, 
                                 is_summary=is_summary, working_dir=working_dir)

        if do_llm_processing:
            # Create review or summary using chatgpt or huggingface model
            print(f"Start {method} using {model} ...")
            if use_chatgpt:
                summary_part, finish_reason = interface_chatgpt(prompt, model=model)
                print(f"Finished {method} using {model} because {finish_reason}")
            else:
                summary_part = interface_huggingface(
                    prompt, model=model, max_tokens=4000)
                print(f"Finished review using {model}")
            output_file.write(f' {method}\n')
            output_file.write(summary_part)
            output_file.write('\n')
        else:
            print(f"Only extracted text, no {method} using {model} was created")
            output_file.write(f'Only extracted text, no {method} using {model} was created')
