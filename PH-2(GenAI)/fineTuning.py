import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import warnings
warnings.filterwarnings("ignore") #Suppresses Python warnings → cleaner output

from datasets import load_dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, TrainingArguments, Trainer
import torch
import time
import evaluate
import pandas as pd
import numpy as np

#loading the dataset
huggingFace_dataset = "knkarthick/dialogsum"
dataset = load_dataset(huggingFace_dataset)

#loading the model and tokenizer
model_name = 'google/flan-t5-base'

# set the device to GPU or CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#Encoder → Decoder architecture
original_model = AutoModelForSeq2SeqLM.from_pretrained(model_name, torch_dtype=torch.bfloat16).to(device)
#Converts text → tokens (numbers)
tokenizer = AutoTokenizer.from_pretrained(model_name, device_map="auto")

#Zero-shot inference
index = 200

dialogue = dataset['train'][index]['dialogue']
summary = dataset['train'][index]['summary']

prompt = f'''
summarize the following dialogue:
{dialogue}
summary:
'''

input = tokenizer(prompt, return_tensors='pt').to(device)
output = tokenizer.decode(
    original_model.generate(
        input['input_ids'],
        max_new_tokens=200
    )[0], skip_special_tokens=True
)

print(f'BASELINE HUMAN SUMMARY:\n{summary}')
print(f'MODEL GENERATION - WITHOUT PROMPT ENGINEERING:\n{output}\n')

#preprocess the dialogue-summary dataset

def tokenize_function(examples):
    start_prompt = f'''summarize the following dialogue:\n'''
    end_prompt = "\nsummary:"
    prompt = [start_prompt + dialogue + end_prompt for dialogue in examples['dialogue']]
    examples['input_ids'] = tokenizer(prompt, truncation = True, padding = 'max_length', return_trensors = 'pt').input_ids
    examples['labels'] = tokenizer(examples['summary'], truncation = True, padding = 'max_length', return_tensors = 'pt').input_ids
    return examples

tokenized_dataset = dataset.map(tokenize_function, batched=True)
tokenized_dataset = tokenized_dataset.remove_columns(['id', 'topic', 'dialogue', 'summary',])

tokenized_dataset = tokenized_dataset.filter(lambda example, index: index % 100 == 0, with_indices=True) #Reduce dataset size for faster training
# print(f"Shapes of the datasets:")
# print(f"Training: {tokenized_dataset['train'].shape}")
# print(f"Validation: {tokenized_dataset['validation'].shape}")
# print(f"Test: {tokenized_dataset['test'].shape}")

# print(tokenized_dataset)

#Finetune model with preprocessed dataset
output_dir = f"dialogue_summary_finetuned_model{str(int(time.time()))}"
training_args = TrainingArguments(
    output_dir = output_dir,
    num_train_epochs = 1, #number of Epochs → 1 epoch means model will see entire training dataset once
    learning_rate = 1e-5, #small learning rate for fine-tuning to avoid large weight updates that could disrupt pre-trained knowledge
    weight_decay = 0.01, #regularization technique to prevent overfitting by adding a penalty to the loss function based on the magnitude of model weights
    logging_steps=1, #log training progress every 1 step
    max_steps=1, #limit total training steps to 1 for quick testing (remove or increase for actual training)
    report_to="none" #disable integration with external logging tools (like WandB or TensorBoard
)

trainer = Trainer(
    model=original_model, 
    args=training_args,
    train_dataset=tokenized_dataset['train'], 
    eval_dataset=tokenized_dataset['validation']
)

trainer.train() #Start fine-tuning the model using the Trainer API, which handles the training loop, optimization, and evaluation internally.
