# review_generator

This is a simple script to generate a review of papers from imported PDF or tex files. 

# Installation

Tested on python 3.8.15

## Requirements
install the following packages:
```pip install PyPDF2 textract nltk openai torch pytorch_pretrained_bert plasTeX```

## OpenAI API key 

You need to get an API key from OpenAI. You can do this by creating an account and generate a key at [OpenAI](https://platform.openai.com/account/api-keys).

Add a environemtn variable called OPENAI_API_KEY with the key as value.
For Mac and Linux: 
```export OPENAI_API_KEY="yourkey``` 

alternatively set it in utils/summary_creator_gpt.py by setting ```openai.api_key = "yourkey```. 

# Usage

Adapt and run ```reviewer.py``` to generate a review or summary. You can also use notebook reviewer.ipynb to run the code. It is basically the same as the python script. 

Change ```input_file``` to the path of the file you want to generate a review for. If you work with a PDf change the keywords list to the correct section headings (you may want to check how they got extracted from the PDF in the extract.txt file). 

To run: 
```python reviewer.py```

I included a print of the finish reason for the GPT model API call. If you get not "because stop" in the command line for a specific section you may want to check if there is a problem with the section file or if the file is to long. The possible values for finish_reason are (see [OpenAI API docs](https://platform.openai.com/docs/guides/chat/introduction)):

stop: API returned complete model output
length: Incomplete model output due to max_tokens parameter or token limit
content_filter: Omitted content due to a flag from our content filters
null: API response still in progress or incomplete

I included a sample PDF and tex file where you can test the script.




