**🧠 Persona-Driven Document Intelligence Engine**
This project is a solution for the Adobe India Hackathon (Round 1B). It's an offline, Docker-based application that analyzes a collection of PDFs and extracts the most relevant sections based on a user's specific role and task.

**🚀 Our Approach**
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

**📁 Project Structure**
FINAL_ROUND1B/
├── Dockerfile
├── README.md
├── requirements.txt
├── input/
│   ├── docs/
│   │   └── ... (PDF files go here)
│   └── challenge1b_input.json
├── output/
└── src/
    ├── __init__.py
    ├── __main__.py
    ├── config.py
    ├── data_models.py
    ├── pdf_parser.py
    ├── semantic_analyzer.py
    └── utils.py

▶️ Execution Instructions
The project is designed to be run with Docker.

Important First Step: Set Up Input Files
You must do this before building the Docker image.

Create an input folder in your project directory.

Inside input, create a docs folder.

Place all your PDF files inside the input/docs/ folder.

Place your challenge1b_input.json file directly inside the input/ folder.

**Step 2: Build the Docker Image**
Once your input files are in place, open your terminal in the FINAL_ROUND1B directory and run:

docker build -t adobe-hackathon .

**Step 3: Run the Container**
This command runs the analysis completely offline:

docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" adobe-hackathon

After it finishes, the results.json file will appear in your output folder.