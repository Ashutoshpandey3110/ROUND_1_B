🧠 Persona-Driven Document Intelligence Engine
This project is a solution for the Adobe India Hackathon (Round 1B). It's an offline, Docker-based application that analyzes a collection of PDFs and extracts the most relevant sections based on a user's specific role and task.

🚀 Our Approach
Our system uses a generalized, three-stage pipeline:

Adaptive Deconstruction: The code first analyzes the structure of the PDFs to identify headings and group the content under them correctly.

Semantic Analysis: It then uses the all-MiniLM-L6-v2 language model to understand the meaning of the user's request and the content of the documents.

Dynamic Ranking: Finally, it ranks the document sections based on how well they match the user's request, boosting the score for sections that contain specific keywords from the job description.

🔧 Technology Stack
Language: Python 3.9

PDF Parsing: PyMuPDF

NLP / Semantic Analysis: sentence-transformers, torch

Data Validation: pydantic

Containerization: Docker

📁 Project Structure
FINAL_ROUND1B/
│
├── Dockerfile
├── README.md         (This file)
├── requirements.txt
│
├── input/
│   ├── docs/
│   └── challenge1b_input.json
│
├── output/
│
└── src/
    ├── __init__.py
    ├── __main__.py
    └── ... (other .py files)

▶️ Execution Instructions
The project is designed to be run with Docker.

**Step 1: Set Up Input Files**

Make sure your input folder is structured correctly:

FINAL_ROUND1B/
└── input/
    ├── docs/
    │   ├── pdf_file_1.pdf
    │   └── pdf_file_2.pdf
    └── challenge1b_input.json

****Step 2: Build the Docker Image**

In your terminal, from the FINAL_ROUND1B directory, run:

docker build -t adobe-hackathon .

**Step 3: Run the Container**

This command runs the analysis completely offline:

docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" adobe-hackathon

After it finishes, the results.json file will appear in your output folder.