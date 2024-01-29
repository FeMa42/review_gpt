import os
import openai
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def create_summary_gpt(text, model='text-davinci-003', max_tokens=2200):
    response = client.completions.create(engine=model,
    prompt=f"Please summarize the following text:\n\n{text}\n",
    temperature=0.5,
    max_tokens=max_tokens,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None)
    summary = response.choices[0].text.strip()
    return summary


def create_summary_chatgpt(text, section="section", model='gpt-3.5-turbo', is_summary=True):
    if is_summary:
        messages = [
            {"role": "system", "content": "You are a helpful assistent for researchers in the field of computer science. You are helping them to summarize their papers."},
            {"role": "user", "content": f'Please summarize the following {section}: \n{text}'},

        ]
    else:
        messages = [
            {"role": "system", "content": "You are a researcher in the field of computer science working as a reviewer for the Springer Applied Intelligence journal."},
            {"role": "user",
                "content": f'Review the following {section} of the paper. Find points that are good and relevant points that need improvement or might not comply to the high standard of this journal. \n{text}'},
        ]
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
