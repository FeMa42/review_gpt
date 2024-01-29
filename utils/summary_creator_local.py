from mlx_lm import load, generate


def create_summary_huggingface(text, model="mlx-community/NeuralBeagle14-7B-mlx", max_tokens=8000, is_summary=True):
    if "NeuralBeagle14-7B-mlx" in model:
        model = "mlx-community/NeuralBeagle14-7B-mlx"
    model, tokenizer = load(model)
    if is_summary:
        messages = [
            {"role": "system", "content": "You are a helpful assistent for researchers in the field of computer science. You are helping them to summarize their papers."},
            {"role": "user", "content": f'Please summarize the following: \n{text}'},

        ]
    else:
        messages = [
            {"role": "system", "content": "You are a researcher in the field of computer science working as a reviewer for the Springer Applied Intelligence journal."},
            {"role": "user",
                "content": f'Review the following sections of the paper. Find points that are good and more importantly find points that need improvement or might not comply to the high standard of this journal. \n{text}'},
        ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)
    # prompt = f"Please summarize the following text:\n\n{text}\n"

    response = generate(model, tokenizer, prompt=prompt,
                        verbose=False, max_tokens=max_tokens)
    # find the next <|im_end|> in the response and remove everything after it
    response = response.split("<|im_end|>")[0]
    return response
