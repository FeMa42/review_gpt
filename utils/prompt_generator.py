from typing import List, Dict, Union
import os 
import torch
from llmlingua import PromptCompressor


def generate_prompt(text: str, compress_prompt: bool = True, compressor_model: str = None, 
                    max_tokens: int = 8000, is_summary: bool = True, working_dir: str = None) -> List[Dict[str, Union[str, bool]]]:
    """
    Generates a prompt for a language model based on the given text.
    
    Args:
        text (str): The input text for which the prompt needs to be generated.
        compress_prompt (bool): Whether to compress the prompt using a PromptCompressor model. Default is True.
        compressor_model (str): The path to the PromptCompressor model file. If not provided, a default model will be used.
        max_tokens (int): The maximum number of tokens allowed in the prompt. Default is 8000.
        is_summary (bool): Whether the task is a summary task or a review task. Default is True.
        working_dir (str): The path to the working directory where the compressed prompt will be saved. 
                           If not provided, the prompt will not be saved to a file.
    
    Returns:
        List[Dict[str, Union[str, bool]]]: A list of messages containing the prompt for the language model.
                                           Each message has a role (system or user) and content (the prompt).
    """
    # Initialize input text and prompts based on task type
    input_text = text
    if is_summary:
        instruction = "Please summarize the following text."
        question = "What is the main content of the previous passages?"
    else:
        instruction = "Review the following paper. Find points that are good and points that need improvement. Provide constructive feedback, be specific and provide examples where possible."
        question = "Is this paper interesting for the audience in the field and are the claims made in the submission supported by accurate, convincing and clear evidence?"
    
    if compress_prompt:
        # Check if MPS is available
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        
        # Initialize PromptCompressor model
        if compressor_model is not None:
            lingua_compressor = PromptCompressor(
                device_map=device, model_name=compressor_model)
        else:
            lingua_compressor = PromptCompressor(device_map=device)

        
        # Compress the prompt using PromptCompressor model
        compressed_prompt = lingua_compressor.compress_prompt(
            input_text,  # .split("\n\n")
            instruction=instruction,
            question=question,
            target_token=max_tokens,
            condition_compare=True,
            condition_in_question='after',
            rank_method='longllmlingua',
            use_sentence_level_filter=False,
            context_budget="+200", # enable dynamic_context_compression_ratio
            dynamic_context_compression_ratio=0.4,
            # reorder_context="sort"
        )
        
        if working_dir is not None:
            # Save compressed prompt to a file
            prompt_path = os.path.join(working_dir, 'prompt.txt')
            with open(prompt_path, 'w', encoding='utf-8') as output_file:
                output_file.write(compressed_prompt["compressed_prompt"])
                output_file.write("\n")
                output_file.write('origin tokens: ' + str(compressed_prompt["origin_tokens"]))
                output_file.write('compressed tokens: ' + str(compressed_prompt["compressed_tokens"]))
                output_file.write('compression ratio: ' + str(compressed_prompt["ratio"]))
        
        final_prompt = compressed_prompt["compressed_prompt"]
    else:
        final_prompt = instruction + "\n" + input_text + "\n" + question
    
    # Create list of messages containing the prompt
    if is_summary:
        messages = [
            {"role": "system", "content": "You are a helpful assistant for researchers in the field of computer science. You are helping them to summarize their papers."},
            {"role": "user", "content": final_prompt},
        ]
    else:
        messages = [
            {"role": "system", "content": "You are a reviewer in the field of computer science for the Transactions on Machine Learning Research. You assess relevance, technical soundness, and clarity of narrative and arguments. You also provide constructive feedback to the authors."},
            {"role": "user", "content": final_prompt},
        ]
    
    return messages