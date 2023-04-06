import os
from utils.pdf_to_text import extract_pdf_text, clean_text, add_spaces, add_linebreaks
from utils.summary_creator_basic import create_summary_tf, create_summary_spacy, create_summary_bart, create_summary_gensim, create_summary_cerebras
from utils.summary_creator_gpt import create_summary_gpt, create_summary_chatgpt
from utils.large_text_handler import split_text_file_by_keywords


def summarize_head(text, summary_method='gensim'):
    finish_reason = ""
    if summary_method == 'gpt':
        summary = create_summary_gpt(text)
    elif summary_method == 'chatgpt':
        summary, finish_reason = create_summary_chatgpt(
            text, model='gpt-3.5-turbo', is_summary=True)
    elif summary_method == 'tf':
        summary = create_summary_tf(text)
    elif summary_method == 'spacy':
        summary = create_summary_spacy(text)
    elif summary_method == 'bart':
        summary = create_summary_bart(text)
    elif summary_method == 'cerebras':
        summary = create_summary_cerebras(text)
    else:
        summary = create_summary_gensim(text)
    return summary, finish_reason


if __name__ == "__main__":
    # pdf input
    input_pdf = '/Users/damian/Downloads/APIN-D-23-00892_reviewer.pdf' # '/Users/damian/soiltdm.pdf'
    projekt_name = 'APIN-D-23-00892'
    working_dir = os.path.join("./texts/", projekt_name)
    if not os.path.isdir(working_dir):
        os.mkdir(working_dir)
    

    # Extract text from PDF
    extract_pdf = False # If false we try to load the text from a file (we try to load extract.txt)
    # we can also load a specific text file
    load_specific_text = False
    input_text = "abstract.txt"  # 'extract.txt', 'abstract.txt', 'extract_cleaned.txt'

    # Clean extracted text
    clean_extracted_text = True
    add_spaces_to_text = False

    # split large text into chunks of 1000 words or based on keywords
    split_large_text = True

    # Summarize text
    summarize_text = True
    summary_method = 'chatgpt'

    # Extract text from the PDF
    extract_path = os.path.join(working_dir, 'extract.txt')
    extract_cleaned_path = os.path.join(working_dir, 'extract_cleaned.txt')
    if extract_pdf:
        print("Extracting text from PDF file")
        text = extract_pdf_text(input_pdf)
        with open(extract_path, 'w') as f:
            f.write(text)
        print("Extracted text from PDF file")
    else:
        print("Reading text from file")
        with open(extract_path, 'r') as f:
            text = f.read()

    if split_large_text is False:
        if clean_extracted_text:
            print("Cleaning extracted text")
            text = clean_text(text, remove_line_breaks=False,
                            remove_refernces=True, remove_math_symbols=True)
        if add_spaces_to_text:
            print("Adding spaces to text")
            text = add_spaces(text)
    
    if clean_extracted_text or add_spaces_to_text:
        print("Saving cleaned text to file")
        with open(extract_cleaned_path, 'w') as f:
            f.write(text)

     # soiltdm
    # keywords = ['Abstract', '1 Introduction',
    #             '2 Background', '3 Method', '4 Related Work', '5 Experiments', 'Conclusion', 'References']
    keywords = ['Abstract', '1 Introduction', '1.1 Reinforcement Learning', '1.2 Manufacturing of semiconductor',
                    '1.3 Process control for semiconductor fabrication',
                    '2 Framework', '2.1 Environments', '2.2 Reward & Return', '2.3 Control',
                    '3E x p e r i m e n t s', '4 Further Research and Discussion', '5 Conclusion']
    if split_large_text and extract_pdf:
        split_text_file_by_keywords(
            text, working_dir, keywords, 
            clean_extracted_chunk=clean_extracted_text, 
            add_spaces_to_chunk=add_spaces_to_text)

    if load_specific_text:
        print("Reading text from specific given file:" + input_text)
        with open(input_text, 'r') as f:
            text = f.read()
    elif extract_pdf is False and clean_extracted_text is False:
        print("Reading text from file:" + input_text)
        # check if the file extracted_cleaned_path if available:
        if os.path.isfile(extract_cleaned_path):
            print("Reading text from file:" + extract_cleaned_path) 
            with open(extract_cleaned_path, 'r') as f:
                text = f.read()
        else:  
            # read from extract_path:
            print("Reading text from file:" + extract_path)
    
    # Summarize the text
    if summarize_text:
        if split_large_text: 
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
            print("found " + str(len(section_files)) + " section files")
            if len(section_files) <= len(keywords):
                print("found less than or equal amount of section files compared to keywords")
                use_keywords = True
            else:
                print("found more section files than keywords")
                use_keywords = False
            summary = ""
            combined_summary_path = os.path.join(
                working_dir, 'combined_summary_' + summary_method + '.txt')
            with open(combined_summary_path, 'w', encoding='utf-8') as output_file:
                for idx, content in enumerate(section_files, start=1):
                    print(f"Summarizing section_{idx}.txt using {summary_method} ...")
                    summary_part, finish_reason = summarize_head(
                        content, summary_method=summary_method)
                    print(f"Finished summarizing section_{idx}.txt using {summary_method} because {finish_reason}")
                    if use_keywords:
                        output_file.write(f'Summary of {keywords[idx-1]} (section_{idx}.txt)\n')
                    else:
                        output_file.write(f'Summary of section_{idx}.txt\n')
                    output_file.write(add_linebreaks(summary_part))
                    output_file.write('\n')
                    summary += summary_part
                    summary += "\n"
        else:
            print("Summarizing text using " + summary_method)
            summary, finish_reason = summarize_head(
                text, summary_method=summary_method)
            print(f"Finished summarizing using {summary_method} because {finish_reason}")

        # Print the summary to the console
        print("##############Summary##############\n")
        print(summary)
        print("##############Summary##############\n")

        # Save the summary to a text file for later use
        summary_path = os.path.join(working_dir, 'summary_' + summary_method + '.txt')
        with open(summary_path, 'w') as f:
            f.write(summary)
