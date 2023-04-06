from gensim.summarization import summarize
from transformers import pipeline
import spacy
from heapq import nlargest
from transformers import BartTokenizer, BartForConditionalGeneration
from utils.pdf_to_text import tokenize_text
from transformers import AutoTokenizer, AutoModelForCausalLM


def create_summary_cerebras(text, max_new_tokens=50):
    tokenizer = AutoTokenizer.from_pretrained("cerebras/Cerebras-GPT-2.7B")# Cerebras-GPT-13B
    model = AutoModelForCausalLM.from_pretrained("cerebras/Cerebras-GPT-2.7B")  # Cerebras-GPT-13B


    text = "Summarize the following text: " + text + "."

    # pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    # generated_text = pipe(text, max_length=50, do_sample=False, no_repeat_ngram_size=2)[0]
    # print(generated_text['generated_text'])

    inputs = tokenizer(text, return_tensors="pt")
    outputs = model.generate(**inputs, num_beams=5,
                             max_new_tokens=max_new_tokens, early_stopping=True,
                             no_repeat_ngram_size=2)
    text_output = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return text_output[0]


def create_summary_bart(text, model_name="facebook/bart-large-cnn"):
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    inputs = tokenizer([text], max_length=1024,
                       return_tensors="pt", truncation=True)
    summary_ids = model.generate(
        inputs["input_ids"], num_beams=8, min_length=400, max_length=1500)

    summary = [tokenizer.decode(s, skip_special_tokens=True,
                                clean_up_tokenization_spaces=False) for s in summary_ids]
    return summary[0]

def create_summary_spacy(text, num_sentences=5):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    sentence_rank = {sent: sent.text for sent in doc.sents}
    ranked = nlargest(num_sentences, sentence_rank, key=sentence_rank.get)

    return ' '.join([sent.text for sent in ranked])


def create_summary_tf(text):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']


def create_summary_gensim(text, summary_ratio=0.2):
    preprocessed_text = tokenize_text(text)
    summary = summarize(preprocessed_text, ratio=summary_ratio)
    return summary
