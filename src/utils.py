"""
Utility Functions

This module contains common helper functions used across the application.
Keeping them separate improves code organization and reusability.
"""

import datetime
import json
from pathlib import Path
from typing import Dict, Any

from .data_models import FinalOutput

def get_timestamp() -> str:
    """
    Generates a current timestamp in ISO 8601 format.

    Returns:
        str: The current timestamp as a string.
    """
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save_results_to_json(output_data: FinalOutput, output_path: Path):
    """
    Serializes the final Pydantic output model to a JSON file.

    Args:
        output_data (FinalOutput): The Pydantic model containing the results.
        output_path (Path): The file path to save the JSON to.
    """
    # Create the output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Use Pydantic's built-in method to convert the model to a dictionary,
    # then dump it to a JSON file with indentation for readability.
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data.dict(), f, indent=4, ensure_ascii=False)
    
    print(f"Successfully saved results to {output_path}")

