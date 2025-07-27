# PDF Heading Detection System

## Overview

This project is an AI-powered system that automatically detects and classifies different heading levels (TITLE, H1, H2, H3) and regular text from PDF documents. Built using machine learning with RandomForest classifier, it analyzes font properties, positioning, and text patterns to accurately categorize content structure.

## Features

🔍 **Smart Heading Detection**: Automatically identifies titles, headings (H1, H2, H3), and regular text  
🤖 **Machine Learning Powered**: Uses RandomForest classifier trained on academic papers  
🎯 **Adaptive Font Analysis**: Works with PDFs of different font sizes and styles  
🧹 **Advanced Filtering**: Removes watermarks, table of contents, and junk symbols  
📄 **Text Merging**: Combines text spans that belong to the same sentence/paragraph  
🔄 **Batch Processing**: Process multiple PDFs automatically  
📊 **JSON Output**: Clean, structured output for easy integration  
🐳 **Docker Ready**: Containerized for easy deployment and reproducibility  

## Technology Stack

- **Python 3.9+**: Core programming language
- **PyMuPDF (fitz)**: PDF text extraction and analysis
- **scikit-learn**: Machine learning (RandomForest classifier)
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **Docker**: Containerization for deployment

## Project Structure

```
pdf-heading-detector/
├── Dockerfile           # Docker container configuration
├── requirements.txt     # Python dependencies
├── main.py             # Main application code
├── README.md           # This file
├── input/              # Place your PDF files here
│   ├── document1.pdf
│   └── document2.pdf
└── output/             # JSON results appear here
    ├── document1_labels.json
    └── document2_labels.json
```

## Algorithm Overview

### 1. **PDF Text Extraction**
- Extracts text with font properties (size, style, position)
- Merges text spans on the same line for better accuracy
- Filters out watermarks, headers, footers, and margins

### 2. **Feature Engineering**
- **Font Size**: Relative to document's average font size
- **Font Style**: Bold detection for emphasis
- **Position**: X, Y coordinates for layout analysis
- **Text Properties**: Length, uppercase ratio, patterns
- **Context**: Page position, document structure

### 3. **Smart Filtering**
- **Watermark Detection**: Removes translucent or margin text
- **TOC Filtering**: Excludes table of contents entries
- **Symbol Cleanup**: Filters junk symbols, page numbers, dots
- **Pattern Recognition**: Identifies numbered sections (1.1, 1.1.1)

### 4. **Machine Learning Classification**
- **Training Data**: Academic papers from arXiv
- **Model**: RandomForest with 100 estimators
- **Features**: Font size, position, formatting, text properties
- **Labels**: TITLE, H1, H2, H3, P (paragraph)

### 5. **Post-Processing**
- **Single Title Rule**: Ensures only one TITLE per document
- **Hierarchy Validation**: Maintains logical heading structure
- **Quality Assurance**: Validates predictions against patterns

## Installation & Usage

### Method 1: Docker (Recommended)

#### Prerequisites
- Docker installed on your system
- PDF files to process

#### Quick Start

1. **Setup directories:**
```bash
mkdir -p input output
```

2. **Add your PDF files:**
```bash
cp your_document.pdf input/
```

3. **Build the Docker image:**
```bash
docker build -t pdf-heading-detector .
```

4. **Run the container:**

**For Linux/Mac:**
```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output:rw pdf-heading-detector
```

**For Windows PowerShell:**
```bash
docker run --rm -v ${PWD}/input:/app/input:ro -v ${PWD}/output:/app/output:rw pdf-heading-detector
```

**For Windows Command Prompt:**
```bash
docker run --rm -v %cd%/input:/app/input:ro -v %cd%/output:/app/output:rw pdf-heading-detector
```

5. **Check results:**
```bash
ls output/
```

#### One-Line Build and Run
```bash
# Linux/Mac
docker build -t pdf-detector . && docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output:rw pdf-detector

# Windows PowerShell  
docker build -t pdf-detector . && docker run --rm -v ${PWD}/input:/app/input:ro -v ${PWD}/output:/app/output:rw pdf-detector
```

### Method 2: Local Python Installation

#### Prerequisites
- Python 3.9 or higher
- pip package manager

#### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Output Format

The system generates JSON files for each processed PDF with the following structure:

```json
[
  {
    "page": 1,
    "text": "Machine Learning in Document Processing",
    "label": "TITLE"
  },
  {
    "page": 1,
    "text": "1. Introduction",
    "label": "H1"
  },
  {
    "page": 1,
    "text":