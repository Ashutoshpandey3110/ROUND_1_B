"""
Configuration and Constants

This module stores all static configuration values for the application,
such as file paths, model names, and processing parameters.
Centralizing these values makes the application easier to manage and modify.
"""

from pathlib import Path

# --- Path Definitions ---
# Using pathlib for OS-agnostic path handling.
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
DOCS_DIR = INPUT_DIR / "docs"
# Corrected the input filename to match the hackathon specification.
PERSONA_FILE = INPUT_DIR / "challenge1b_input.json"
OUTPUT_FILE = OUTPUT_DIR / "results.json"
MODEL_DIR = BASE_DIR / "models"

# --- Model Configuration ---
# The name of the sentence-transformer model.
MODEL_NAME = 'all-MiniLM-L6-v2'

# --- CORRECTED LINE ---
# Instead of a local path, we provide the model's name directly.
# The library will handle downloading and caching it automatically.
MODEL_PATH = MODEL_NAME


# --- Processing Parameters ---
# The target word count for semantic chunking. This is a balance between
# having enough context and not diluting the chunk's meaning.
CHUNK_TARGET_WORD_COUNT = 250

# The number of top-ranked sections to include in the final output.
TOP_N_SECTIONS = 10

# The number of sub-section analyses to perform and include.
TOP_N_SUB_SECTIONS = 15

# --- PDF Parsing Heuristics ---
# These multipliers are used to classify headings based on their font size
# relative to the document's main body text font size.
H1_SIZE_MULTIPLIER = 1.5
H2_SIZE_MULTIPLIER = 1.2