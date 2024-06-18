# --------------------------------------------------------------
# Import Modules
# --------------------------------------------------------------

import os
import json
import openai
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --------------------------------------------------------------
# Load OpenAI API Token From the .env File
# --------------------------------------------------------------

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --------------------------------------------------------------
# Function Descriptions for Function Calling
# --------------------------------------------------------------

function_descriptions = [
    {
        "name": "generate_variation",
        "description": "Generate a variation of the given message while preserving its meaning, functionality, and key elements.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to be varied."
                },
                "role": {
                    "type": "string",
                    "description": "The role of the message (e.g., user, assistant, system, tools, tool_use, tool_output)."
                },
                "language": {
                    "type": "string",
                    "description": "The programming language of the code, if applicable."
                },
                "context": {
                    "type": "string",
                    "description": "Additional context or description about the message or code."
                },
                "preserve_structure": {
                    "type": "boolean",
                    "description": "Whether to preserve the structural elements of the message."
                },
                "target_audience": {
                    "type": "string",
                    "description": "The target audience for the message (e.g., beginners, experts)."
                },
                "length_constraint": {
                    "type": "integer",
                    "description": "Any length constraints for the variation."
                },
                "include_documentation": {
                    "type": "boolean",
                    "description": "Whether to include documentation strings."
                }
            },
            "required": ["message", "role", "language", "context", "preserve_structure", "include_documentation"]
        }
    }
]

# --------------------------------------------------------------
# Load and Process Notebooks
# --------------------------------------------------------------

def load_notebook(notebook_path):
    """
    Load a Jupyter notebook from a JSON file.

    Args:
        notebook_path (str): Path to the JSON file containing the notebook.

    Returns:
        dict or None: Loaded notebook as a Python dictionary if successful, 
                      None if file not found or JSON decoding error occurs.
    """
    try:
        with open(notebook_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {notebook_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {notebook_path}: {e}")
        return None
    
def extract_cells(notebook):
    """
    Extract cells from a Jupyter notebook.

    Args:
        notebook (dict): The notebook loaded as a Python dictionary.

    Returns:
        list: List of cells (dict) from the notebook if notebook is not None, 
              otherwise an empty list.
    """
    return notebook['cells'] if notebook else []

def save_variations(variations, output_path, original_notebook):
    """
    Save variations of notebook cells to a new JSON file.

    Args:
        variations (list): List of dictionaries containing original and varied cells.
        output_path (str): Path to save the varied notebook JSON file.
        original_notebook (dict): Original notebook loaded as a Python dictionary.

    Returns:
        None
    """
    try:
        for i, cell in enumerate(original_notebook['cells']):
            cell_type = cell['cell_type']
            if cell_type in ['code', 'markdown', 'system', 'tools', 'user', 'assistant', 'tool_use', 'tool_output']:
                cell['source'] = variations[i]['variation'].splitlines(keepends=True)
        with open(output_path, 'w') as f:
            json.dump(original_notebook, f, indent=4)
        print(f"Variations saved to {output_path}")
    except IOError as e:
        print(f"Error saving variations to {output_path}: {e}")

# --------------------------------------------------------------
# Generate Variations with Function Calling
# --------------------------------------------------------------

def generate_variation_with_function_call(message, role, language, context,
                                          preserve_structure, include_documentation,
                                          target_audience="general", length_constraint=None):
    """
    Generate a variation of a given message using the OpenAI GPT-4 model.

    Args:
        message (str): The message to be varied.
        role (str): The role of the message (e.g., code, markdown).
        language (str): The programming language of the code (if applicable).
        context (str): Additional context or description about the message or code.
        preserve_structure (bool): Whether to preserve the structural elements of the message.
        include_documentation (bool): Whether to include documentation strings.
        target_audience (str, optional): The target audience for the message (default is "general").
        length_constraint (int, optional): Any length constraints for the variation.

    Returns:
        str: Generated variation of the message as a string.
    """
    
    
    prompt = f"""
    You are a helpful assistant that generates variations of messages while keeping their meaning and functionality the same. 
    Please vary the following {role} message while preserving its core elements, functionality, and including necessary documentation strings:
    {message}
    
    Context: {context}
    Programming Language: {language}
    Preserve Structure: {preserve_structure}
    Target Audience: {target_audience}
    Length Constraint: {length_constraint}
    Include Documentation: {include_documentation}
    """

    try:
        completion = openai.completions.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            n=1,
            stop=None
        )

        if 'choices' in completion and len(completion['choices']) > 0:
            return completion.choices[0].text.strip()

        return message

    except openai.Error as e:
        print(f"OpenAI API error: {e}")
        return message

def process_cells_with_function_call(cells):
    """
    Process each cell in a list of notebook cells, generating variations where applicable.

    Args:
        cells (list): List of dictionaries representing notebook cells.

    Returns:
        list: List of dictionaries containing original and varied cells.
    """
    varied_cells = []

    for cell in cells:
        role = cell['cell_type']
        source = ''.join(cell['source'])
        
        if role in ['code', 'markdown', 'system', 'tools', 'user', 'assistant', 'tool_use', 'tool_output']:
            variation = generate_variation_with_function_call(
                message=source,
                role=role,
                language="python",  # You can adjust or derive this value dynamically
                context="This is part of a Jupyter notebook.",
                preserve_structure=True,
                include_documentation=True,
                target_audience="general",
                length_constraint=150
            )
            varied_cells.append({'role': role, 'original': source, 'variation': variation})
        else:
            varied_cells.append({'role': role, 'original': source, 'variation': source})  # No change for other cells

    return varied_cells

# --------------------------------------------------------------
# Main Function with Function Calling
# --------------------------------------------------------------

def main_with_function_call():
    """
    Main function to orchestrate the process of loading, processing, generating variations, and saving a Jupyter notebook.

    Args:
        None

    Returns:
        None
    """
    input_path = 'notebook/Sample1.ipynb'
    output_path = 'varied/notebook.json'

    notebook = load_notebook(input_path)
    cells = extract_cells(notebook)
    variations = process_cells_with_function_call(cells)
    save_variations(variations, output_path, notebook)
    print(f"Variations saved to {output_path}")

if __name__ == '__main__':
    main_with_function_call()
