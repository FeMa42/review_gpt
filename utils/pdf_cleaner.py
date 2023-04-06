import re
from pytorch_pretrained_bert import BertTokenizer, BertForMaskedLM


def remove_line_breaks(text):
    return text.replace("\n", " ")

def clean_text(text, remove_line_breaks=True, remove_refernces=True, remove_math_symbols=True):
    # Remove line breaks
    if remove_line_breaks:
        text = remove_line_breaks(text)
    # text = text.replace("\n", " ")

    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text)

    # Remove unwanted characters (e.g., hyphens, underscores)
    text = re.sub(r"[-_]", "", text)

    if remove_refernces:
        # Remove references like [1]
        text = re.sub(r"\[\d+\]", "", text)
        # Remove everything inside bracket parentheses, including the brackets themselves
        text = re.sub(r'\[.*?\]', '', text)
        # Remove everything inside parentheses, including the parentheses themselves
        text = re.sub(r'\(.*?\)', '', text)
        # Remove everything inside { parentheses, including the parentheses themselves
        text = re.sub(r'\{.*?\}', '', text)
        # Remove single bracket parentheses
        text = re.sub(r'\[', '', text)
        text = re.sub(r'\]', '', text)
        # Remove single parentheses
        text = re.sub(r'\(', '', text)
        text = re.sub(r'\)', '', text)

        # remove multiple periods
        text = re.sub(r"\.{2,}", "\.", text)
        text = re.sub(r"\. \.", "\.", text)
        text = re.sub(r"\.\s+\.", "\.", text)

    if remove_math_symbols:
        # Remove math symbols
        text = re.sub(r"µ", "", text)
        text = re.sub(r"∆", "", text)
        text = re.sub(r"∑", "", text)
        text = re.sub(r"∏", "", text)
        text = re.sub(r"∞", "", text)
        text = re.sub(r"√", "", text)
        text = re.sub(r"⇡", "", text)
        text = re.sub(r"✓", "", text)
        text = re.sub(r"⇒", "", text)
        text = re.sub(r"⇡", "", text)
        text = re.sub(r"⇠", "", text)
        text = re.sub(r"⇢", "", text)
        text = re.sub(r"⇣", "", text)
        text = re.sub(r"\|", "", text)
        text = re.sub(r"=", "", text)
        text = re.sub(r"≤", "", text)
        text = re.sub(r"≥", "", text)
        text = re.sub(r"≠", "", text)
        text = re.sub(r"≡", "", text)
        text = re.sub(r"≈", "", text)

    # Remove incorrectly imported equations
    # This example assumes equations start with "$" and end with "$"
    # Adjust the pattern as needed for your specific use case
    # text = re.sub(r"\$[^\$]*\$", "", text)

    return text.strip()


def add_linebreaks(text):
    # Split the text into words
    words = text.split()
    # Insert line break every 20 words
    output_text = ""
    for i, word in enumerate(words):
        output_text += word + " "
        if (i + 1) % 20 == 0:
            output_text += "\n"
    return output_text.strip()


def add_spaces(text):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForMaskedLM.from_pretrained('bert-base-uncased')
    model.eval()

    tokens = tokenizer.tokenize(text)
    new_tokens = []
    for token in tokens:
        if token.startswith("##"):
            token = token[2:]
        else:
            token = " " + token
        new_tokens.append(token)

    return "".join(new_tokens).strip()
