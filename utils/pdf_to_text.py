import os
import PyPDF2
import fitz  # PyMuPDF uses the 'fitz' namespace
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from utils.large_text_handler import split_text_file_by_keywords


def pdf_to_sections(pdf_path, working_dir, keywords):

    text = extract_pdf_text(pdf_path)
    extract_path = os.path.join(working_dir, 'extract.txt')
    with open(extract_path, 'w') as f:
                f.write(text)
    sections = split_text_file_by_keywords(
        text, working_dir, keywords,
        clean_extracted_chunk=True,
        add_spaces_to_chunk=False)
    
    return sections

def extract_pdf_text(pdf_path, use_legacy=False):
    if use_legacy:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                # page = pdf_reader.getPage(page_num)
                text += page.extract_text()
    else:
        doc = fitz.open(pdf_path)
        text = ""

        for page in doc:
            text += page.get_text("text")
    return text


def tokenize_text(text):
    download_nltk_resources()
    # Tokenize sentences
    sentences = sent_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    filtered_sentences = []
    for sent in sentences:
        words = word_tokenize(sent)
        filtered_words = [
            word for word in words if word.lower() not in stop_words]
        filtered_sentences.append(" ".join(filtered_words))

    # Join sentences back into a single string
    preprocessed_text = " ".join(filtered_sentences)
    return preprocessed_text


def download_nltk_resources():
    nltk.download('punkt')
    nltk.download('stopwords')
