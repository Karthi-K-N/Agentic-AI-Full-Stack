"""
Utility functions for the Agentic AI Chart Generation Lab.

This module provides helper functions to:
- Load and prepare datasets
- Display results in notebook format
- Interact with LLM APIs (OpenAI and Anthropic)
- Handle image encoding and vision-based analysis
"""

import os
import re
import json
import base64
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, Any, Dict
from dotenv import load_dotenv


def load_and_prepare_data(csv_path: str) -> pd.DataFrame: 
    """ Load and prepare the coffee sales dataset. 
    Adds computed columns: year, quarter, and month from the datetime column. 
    Args: csv_path (str): 
        Path to the CSV file containing coffee sales data. 
    Returns: 
        pd.DataFrame: 
            DataFrame with original columns plus year, quarter, and month. 
        Raises: 
            FileNotFoundError: 
                If the CSV file does not exist. 
            ValueError: 
                If required columns are missing. 
    """ 
    if not os.path.exists(csv_path): 
        raise FileNotFoundError(f"CSV file not found: {csv_path}") 
    
    # Load the CSV file 
    df = pd.read_csv(csv_path) 
    # Ensure 'date' column exists and convert to datetime if not already 
    if 'date' not in df.columns: 
        raise ValueError("CSV must contain a 'date' column") 
    
    
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        # Extract time in HH:MM format
        df['time'] = df['datetime'].dt.strftime('%H:%M')
        # Drop the datetime column as it's no longer needed
        df = df.drop(columns=['datetime'])
    
    df = df.rename(columns={'money' : 'price'})
    df['date'] = pd.to_datetime(df['date']) 
    # Extract year, quarter, and month from the date column 
    df['year'] = df['date'].dt.year 
    df['quarter'] = df['date'].dt.quarter 
    df['month'] = df['date'].dt.month 
    df = df[['date','time','cash_type','card','price','coffee_name','quarter','month','year']]

    return df

def print_html(
    content: Any,
    title: str = "",
    is_image: bool = False
) -> None:
    """
    Display content in a clean, readable HTML format within the notebook.
    
    Handles:
    - DataFrames: displays as formatted HTML tables
    - Images: loads and displays images from file paths
    - Strings/Code: displays as preformatted text
    
    Args:
        content (Any): The content to display (DataFrame, file path, or string).
        title (str, optional): A title to display above the content.
        is_image (bool, optional): If True, treats content as an image file path.
    """
    from IPython.display import display, HTML, Image
    
    # Display title if provided
    if title:
        title_html = f"<h3 style='margin-top: 20px; margin-bottom: 10px; color: #2c3e50;'>{title}</h3>"
        display(HTML(title_html))
    
    if is_image:
        # Display image from file path
        if isinstance(content, str) and os.path.exists(content):
            display(Image(filename=content))
        else:
            error_msg = f"<p style='color: red;'>Image not found: {content}</p>"
            display(HTML(error_msg))
    
    elif isinstance(content, pd.DataFrame):
        # Display DataFrame as HTML table
        html_table = content.to_html(
            escape=False,
            classes="table table-striped",
            index=True
        )
        styled_html = f"""
        <div style='overflow-x: auto; margin: 10px 0;'>
            {html_table}
        </div>
        """
        display(HTML(styled_html))
    
    else:
        # Display as preformatted text (for code, strings, etc.)
        if isinstance(content, str):
            # Check if it looks like code (contains common programming patterns)
            formatted_content = content.replace("<", "&lt;").replace(">", "&gt;")
            code_html = f"""
            <pre style='background-color: #f5f5f5; padding: 12px; border-radius: 4px; 
                        overflow-x: auto; border-left: 4px solid #007bff; margin: 10px 0;
                        font-family: "Courier New", monospace; font-size: 12px; line-height: 1.4;'>
            {formatted_content}
            </pre>
            """
            display(HTML(code_html))
        else:
            # Fallback for other types
            text_html = f"<p>{str(content)}</p>"
            display(HTML(text_html))


def get_response(model: str, prompt: str) -> str:
    """
    Get a response from an LLM (OpenAI or similar API).
    
    Supports models like:
    - 'gpt-4o-mini'
    - 'gpt-4o'
    - 'o4-mini'
    
    Args:
        model (str): The model name (e.g., 'gpt-4o-mini').
        prompt (str): The prompt to send to the model.
    
    Returns:
        str: The model's response.
    
    Raises:
        ValueError: If the API key is not set.
        Exception: If the API call fails.
    """
    from openai import OpenAI

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    

    client = OpenAI()

    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=4096
    )

    print(response.output[0].content[0].text)
    
    return response.output[0].content[0].text


def encode_image_b64(image_path: str) -> Tuple[str, str]:
    """
    Encode an image file to base64 for API submission.
    
    Args:
        image_path (str): Path to the image file (PNG, JPG, GIF, WebP).
    
    Returns:
        Tuple[str, str]: A tuple of (media_type, base64_string).
                         media_type is one of: 'image/png', 'image/jpeg', 'image/gif', 'image/webp'.
    
    Raises:
        FileNotFoundError: If the image file does not exist.
        ValueError: If the image format is not supported.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Determine media type based on file extension
    ext = Path(image_path).suffix.lower()
    media_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    
    if ext not in media_type_map:
        raise ValueError(f"Unsupported image format: {ext}. Supported: {list(media_type_map.keys())}")
    
    media_type = media_type_map[ext]
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = base64.standard_b64encode(image_file.read()).decode("utf-8")
    
    return media_type, image_data


def image_openai_call(
    model_name: str,
    prompt: str,
    media_type: str,
    b64_image: str
) -> str:
    """
    Call OpenAI's vision API with an image.
    
    Args:
        model_name (str): The model to use (e.g., 'gpt-4o-mini', 'gpt-4-vision').
        prompt (str): The text prompt to send alongside the image.
        media_type (str): MIME type of the image (e.g., 'image/png').
        b64_image (str): Base64-encoded image data.
    
    Returns:
        str: The model's response.
    
    Raises:
        ValueError: If the API key is not set.
        Exception: If the API call fails.
    """
    import openai
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = openai.OpenAI(api_key=api_key)
    
    # Normalize model name
    if "o4" in model_name:
        model_name = model_name.replace("o4", "o1")
    
    response = client.messages.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=4096
    )
    
    return response.content[0].text


def image_anthropic_call(
    model_name: str,
    prompt: str,
    media_type: str,
    b64_image: str
) -> str:
    """
    Call Anthropic's Claude API with an image (vision capabilities).
    
    Args:
        model_name (str): The model to use (e.g., 'claude-sonnet-4-6', 'claude-opus').
        prompt (str): The text prompt to send alongside the image.
        media_type (str): MIME type of the image (e.g., 'image/png').
        b64_image (str): Base64-encoded image data.
    
    Returns:
        str: The model's response.
    
    Raises:
        ValueError: If the API key is not set.
        Exception: If the API call fails.
    """
    import anthropic
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Normalize model name
    if "claude" not in model_name.lower():
        model_name = f"claude-{model_name}"
    
    response = client.messages.create(
        model=model_name,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    
    return response.content[0].text


def ensure_execute_python_tags(code_body: str) -> str:
    """
    Ensure that Python code is wrapped in <execute_python> tags.
    
    If the code already contains the tags, returns as-is.
    Otherwise, wraps the code with the tags.
    
    Args:
        code_body (str): Python code as a string.
    
    Returns:
        str: Code wrapped with <execute_python> tags.
    """
    code_body = code_body.strip()
    
    if code_body.startswith("<execute_python>") and code_body.endswith("</execute_python>"):
        return code_body
    
    return f"<execute_python>\n{code_body}\n</execute_python>"


def extract_code_from_tags(response: str) -> Optional[str]:
    """
    Extract Python code from <execute_python> tags in the LLM response.
    
    Args:
        response (str): The LLM's response containing tagged code.
    
    Returns:
        Optional[str]: Extracted code, or None if no tags found.
    """
    match = re.search(r"<execute_python>([\s\S]*?)</execute_python>", response)
    if match:
        return match.group(1).strip()
    return None


def parse_json_from_response(response: str) -> Optional[Dict]:
    """
    Extract and parse JSON from an LLM response.
    
    Attempts to find and parse a JSON object from the response text.
    
    Args:
        response (str): The LLM's response.
    
    Returns:
        Optional[Dict]: Parsed JSON object, or None if no valid JSON found.
    """
    # Try to find JSON in the response
    match = re.search(r"\{[\s\S]*\}", response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters.
    
    Args:
        filename (str): The filename to sanitize.
    
    Returns:
        str: Sanitized filename.
    """
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "_", filename)
    return sanitized


def verify_csv_columns(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Verify that a DataFrame has all required columns.
    
    Args:
        df (pd.DataFrame): The DataFrame to check.
        required_columns (list): List of required column names.
    
    Returns:
        bool: True if all required columns are present, False otherwise.
    """
    missing = set(required_columns) - set(df.columns)
    if missing:
        print(f"Warning: Missing columns: {missing}")
        return False
    return True


def get_dataframe_schema(df: pd.DataFrame) -> Dict[str, str]:
    """
    Get a summary schema of a DataFrame (column names and types).
    
    Args:
        df (pd.DataFrame): The DataFrame to analyze.
    
    Returns:
        Dict[str, str]: Dictionary mapping column names to their data types.
    """
    return {col: str(df[col].dtype) for col in df.columns}
