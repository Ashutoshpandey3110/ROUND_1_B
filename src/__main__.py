"""
Main Execution Script

This script serves as the entry point for the application. It orchestrates
the entire pipeline:
1. Loads configuration and input data.
2. Initializes the PDF parser and semantic analyzer.
3. Processes all documents to create a corpus of text chunks.
4. Encodes the persona and the corpus into vectors.
5. Ranks the chunks based on relevance.
6. Synthesizes the results into the final JSON output format.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from . import config, utils
from .data_models import PersonaInput, FinalOutput, MetadataOutput, ExtractedSectionOutput, SubSectionAnalysisOutput
from .pdf_parser import parse_document, chunk_sections
from .semantic_analyzer import SemanticAnalyzer

def run_pipeline():
    """
    The main function that executes the entire intelligence pipeline.
    """
    print("--- Starting Persona-Driven Document Intelligence Pipeline ---")

    # 1. Load Inputs
    print(f"Loading persona from {config.PERSONA_FILE}...")
    try:
        with open(config.PERSONA_FILE, 'r') as f:
            persona_json = json.load(f)

        # CORRECTED PART: Extract the string values from the nested JSON
        persona_data = {
            "persona": persona_json["persona"]["role"],
            "job_to_be_done": persona_json["job_to_be_done"]["task"]
        }
        persona_input = PersonaInput(**persona_data)

    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error: Could not load or parse persona.json. Check file format. Details: {e}")
        return

    pdf_files = list(config.DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        print("Error: No PDF files found in /input/docs/. Aborting.")
        return
    print(f"Found {len(pdf_files)} PDF documents to process.")
    doc_names = [p.name for p in pdf_files]

    # 2. Initialize Core Components
    analyzer = SemanticAnalyzer(model_path=str(config.MODEL_PATH))

    # 3. Process all documents
    print("Parsing and chunking all documents...")
    all_chunks = []
    for pdf_path in pdf_files:
        print(f"  - Processing {pdf_path.name}")
        sections = parse_document(pdf_path)
        chunks = chunk_sections(sections)
        all_chunks.extend(chunks)
    
    if not all_chunks:
        print("Error: No text chunks could be extracted from the documents. Aborting.")
        return

    print(f"Total chunks created: {len(all_chunks)}")

    # 4. Semantic Analysis
    print("Creating query vector from persona...")
    query_vector = analyzer.create_query_vector(persona_input)

    print("Encoding document corpus...")
    corpus_embeddings = analyzer.encode_corpus(all_chunks)

    print("Ranking chunks by relevance...")
    relevance_scores = analyzer.rank_chunks(query_vector, corpus_embeddings)

    # 5. Synthesize Results
    print("Synthesizing final output...")
    
    # Combine chunks with their scores and sort
    scored_chunks = sorted(
        zip(all_chunks, relevance_scores.tolist()),
        key=lambda x: x[1],
        reverse=True
    )

    # --- Build Extracted Sections Output ---
    extracted_sections_output: List[ExtractedSectionOutput] = []
    processed_sections = set()
    rank = 1
    for chunk, score in scored_chunks:
        section_id = (chunk['doc_name'], chunk['section_title'])
        if section_id not in processed_sections:
            extracted_sections_output.append(
                ExtractedSectionOutput(
                    document=chunk['doc_name'],
                    page_number=chunk['page_number'],
                    section_title=chunk['section_title'],
                    importance_rank=rank
                )
            )
            processed_sections.add(section_id)
            rank += 1
        if len(extracted_sections_output) >= config.TOP_N_SECTIONS:
            break

    # --- Build Sub-section Analysis Output ---
    sub_section_analysis_output: List[SubSectionAnalysisOutput] = []
    top_chunks_for_refinement = scored_chunks[:config.TOP_N_SUB_SECTIONS]
    for chunk, score in top_chunks_for_refinement:
        refined_text = analyzer.refine_sub_section(chunk['text'], query_vector)
        sub_section_analysis_output.append(
            SubSectionAnalysisOutput(
                document=chunk['doc_name'],
                page_number=chunk['page_number'],
                refined_text=refined_text
            )
        )

    # --- Assemble Final JSON ---
    final_output = FinalOutput(
        metadata=MetadataOutput(
            input_documents=doc_names,
            persona=persona_input.persona,
            job_to_be_done=persona_input.job_to_be_done,
            processing_timestamp=utils.get_timestamp()
        ),
        extracted_section=extracted_sections_output,
        sub_section_analysis=sub_section_analysis_output
    )

    # 6. Save Output
    utils.save_results_to_json(final_output, config.OUTPUT_FILE)
    print("--- Pipeline Finished Successfully ---")


if __name__ == "__main__":
    # This block allows the script to be run directly
    # The Docker entrypoint calls `python -m src.__main__` which executes this.
    run_pipeline()