import os
import openai
from openai import OpenAI
from mlx_lm import load, generate

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def interface_chatgpt(messages, model='gpt-3.5-turbo'):
    try:
        response = client.chat.completions.create(model=model,
        messages=messages)
        finish_reason = response.choices[0].finish_reason
        summary = response.choices[0].message.content
        return summary, finish_reason
    except openai.InvalidRequestError as e:
        error_message = e.json_body['error']['message']
        error_message = 'Error: ' + error_message
        print("Error: OpenAI API request failed. Error message:", error_message) 
        return f'No content - {error_message}', error_message


def interface_huggingface(messages, model="NeuralBeagle14-7B-mlx", max_tokens=8000):
    if "NeuralBeagle14-7B-mlx" in model:
        model = "mlx-community/NeuralBeagle14-7B-mlx"
    elif "NeuralBeagle14-7B" in model:
        model = "mlabonne/NeuralBeagle14-7B"
    model, tokenizer = load(model)
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)

    response = generate(model, tokenizer, prompt=prompt,
                        verbose=False, max_tokens=max_tokens)
    # find the next <|im_end|> in the response and remove everything after it
    response = response.split("<|im_end|>")[0]
    return response
