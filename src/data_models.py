"""
Pydantic Data Models

This module defines the data structures for input (persona.json) and output (results.json)
files. Using Pydantic ensures that the data conforms to the expected schema,
providing automatic validation and clear error messages if the format is incorrect.
This is crucial for building a robust and predictable data pipeline.
"""

from pydantic import BaseModel, Field
from typing import List

# --- Input Models ---

class PersonaInput(BaseModel):
    """
    Defines the structure of the input persona.json file.
    """
    persona: str = Field(..., description="The role or title of the user.")
    job_to_be_done: str = Field(..., description="The user's specific goal or task.")


# --- Output Models ---
# These models are nested to represent the final JSON structure accurately.

class MetadataOutput(BaseModel):
    """
    Defines the metadata section of the output JSON.
    """
    input_documents: List[str] = Field(..., description="List of processed PDF filenames.")
    persona: str
    job_to_be_done: str
    processing_timestamp: str = Field(..., description="ISO 8601 timestamp of when processing finished.")

class ExtractedSectionOutput(BaseModel):
    """
    Defines the structure for a single extracted section.
    """
    document: str = Field(..., description="Source document filename.")
    page_number: int = Field(..., description="Page number where the section begins.")
    section_title: str = Field(..., description="The identified title of the section.")
    importance_rank: int = Field(..., description="The rank of the section's relevance (1 is highest).")

class SubSectionAnalysisOutput(BaseModel):
    """
    Defines the structure for a single sub-section analysis result.
    """
    document: str = Field(..., description="Source document filename.")
    page_number: int = Field(..., description="Page number of the refined text.")
    refined_text: str = Field(..., description="The single most relevant sentence extracted.")

class FinalOutput(BaseModel):
    """
    The root model for the final results.json file.
    This model composes the other models into the final required structure.
    """
    metadata: MetadataOutput
    extracted_section: List[ExtractedSectionOutput]
    sub_section_analysis: List[SubSectionAnalysisOutput]
