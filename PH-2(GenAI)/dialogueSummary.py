from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GenerationConfig

## datasets
huggingFace_dataset = load_dataset("knkarthick/dialogsum")

# printing couple of datas
dash_line = '-'.join('' for i in range(100))
example_indices = [40, 200]
# for i, index in enumerate(example_indices):
#     print("-" * 50)
#     print(f"Example {i+1}:")
#     print("-" * 50)
#     print("Dialogue:", huggingFace_dataset['train'][index]['dialogue'])
#     print("-" * 50)
#     print("Summary:", huggingFace_dataset['train'][index]['summary'])
#     print("-" * 50)

# Load the model
model_name= 'google/flan-t5-base'
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

'''
# testing with simple statement 
statement = "Have you been a class leader?"

sentence_encoder = tokenizer(statement, return_tensors="pt")
sentence_decoder = tokenizer.decode(sentence_encoder['input_ids'][0], skip_special_tokens=True)

print(sentence_decoder)'''

'''
# without any prompt
for i, index in enumerate(example_indices):
    dialogue = huggingFace_dataset['train'][index]['dialogue']
    summary = huggingFace_dataset['train'][index]['summary']

    sentence_encoder = tokenizer(dialogue, return_tensors='pt')
    sentence_decoder = tokenizer.decode(model.generate(
        sentence_encoder['input_ids'], max_new_tokens=50
    )[0], skip_special_tokens=True)

    print(dash_line)
    print('Example ', i + 1)
    print(dash_line)
    print(f'INPUT PROMPT:\n{dialogue}')
    print(dash_line)
    print(f'BASELINE HUMAN SUMMARY:\n{summary}')
    print(dash_line)
    print(f'MODEL GENERATION - WITHOUT PROMPT ENGINEERING:\n{sentence_decoder}\n')'''

"""
# Zero-shot prompting

for i, index in enumerate(example_indices):
    dialogue = huggingFace_dataset['train'][index]['dialogue']
    summary = huggingFace_dataset['train'][index]['summary']
    prompt = f'''Summarize the following dialogue: 
            {dialogue}
            Summary:'''
    sentence_encoder = tokenizer(prompt, return_tensors='pt')
    sentence_decoder = tokenizer.decode(model.generate(
        sentence_encoder['input_ids'], max_new_tokens=50
    )[0], skip_special_tokens=True)

    print(dash_line)
    print('Example ', i + 1)
    print(dash_line)
    print(f'INPUT PROMPT:\n{dialogue}')
    print(dash_line)
    print(f'BASELINE HUMAN SUMMARY:\n{summary}')
    print(dash_line)
    print(f'MODEL GENERATION - WITHOUT PROMPT ENGINEERING:\n{sentence_decoder}\n')"""

# one-shot and Few-shot prompting

def make_prompt(example_indices, example_indices_summary):
    prompt = ''
    for x, index in enumerate(example_indices):
        dialogue = huggingFace_dataset['train'][index]['dialogue']
        summary = huggingFace_dataset['train'][index]['summary']
        prompt += f'''
               Dialogue: {dialogue}
               What is going on? {summary}'''
    
    dialogue = huggingFace_dataset['train'][example_indices_summary]['dialogue']
    prompt += f'''
               Dialogue: {dialogue}
               What is going on?'''
    return prompt
example_indices = [40, 80, 120] #Few-shot prompting with 3 examples
# example_indices = [40] #One-shot prompting with 1 example
example_indices_summary = 200

few_shot_prompt = make_prompt(example_indices, example_indices_summary)


summary = huggingFace_dataset['train'][example_indices_summary]['summary']

input = tokenizer(few_shot_prompt, return_tensors='pt')
output = tokenizer.decode(model.generate(
    input['input_ids'], max_new_tokens=50
)[0], skip_special_tokens=True)

print(dash_line)
print(f'INPUT PROMPT:\n{few_shot_prompt}')
print(dash_line)
print(f'BASELINE HUMAN SUMMARY:\n{summary}')
print(dash_line)
print(f'MODEL GENERATION - WITHOUT PROMPT ENGINEERING:\n{output}\n')

generation_config = GenerationConfig(max_new_tokens = 50, do_sample = True, top_k = 50, temperature = 1.5)

input = tokenizer(few_shot_prompt, return_tensors='pt')
output = tokenizer.decode(model.generate(
    input['input_ids'], generation_config = generation_config
)[0], skip_special_tokens=True)

print(dash_line)
print(f'BASELINE HUMAN SUMMARY:\n{summary}')
print(dash_line)
print(f'MODEL GENERATION - WITHOUT PROMPT ENGINEERING:\n{output}\n')