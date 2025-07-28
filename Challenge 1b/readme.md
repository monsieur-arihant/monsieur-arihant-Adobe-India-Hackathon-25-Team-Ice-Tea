# Challenge 1b: Multi-Collection PDF Analysis System

## 🎯 Overview

An intelligent document analysis system that extracts and prioritizes relevant sections from PDF collections based on specific personas and their job-to-be-done. The system processes multiple document collections simultaneously, providing persona-driven content analysis with importance ranking.

**Theme**: "Connect What Matters — For the User Who Matters"

## 🏗️ System Architecture

```
├── main.py                         # Core analysis system
├── setup_collections.py            # Collection structure generator  
├── test_system.py                  # Comprehensive test suite
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
├── approach_explanation.md         # Technical methodology
├── EXECUTION_INSTRUCTIONS.md       # Detailed setup guide
└── Challenge_1b/                   # Generated collections structure
    ├── Collection 1/               # Travel Planning
    ├── Collection 2/               # Adobe Acrobat Learning
    └── Collection 3/               # Recipe Collection
```

## ⚡ Quick Start

```bash
# 1. Setup environment
pip install -r requirements.txt

# 2. Create collections structure
python setup_collections.py

# 3. Add PDF files to each collection's PDFs/ directory
#    (See README files in each PDFs/ directory for requirements)

# 4. Run analysis
python main.py --collections_dir Challenge_1b/

# 5. Check results in Challenge_1b/Collection X/challenge1b_output.json
```

## 📊 Sample Collections

### Collection 1: Travel Planning South France
- **Challenge ID**: `round_1b_002`
- **Persona**: Travel Planner specializing in group coordination
- **Task**: Plan 4-day trip for 10 college friends to South of France
- **Documents**: 7 travel guides (Nice, Provence, Côte d'Azur, etc.)
- **Key Outputs**: Budget-friendly activities, group accommodations, transportation

### Collection 2: Adobe Acrobat HR Forms  
- **Challenge ID**: `round_1b_003`
- **Persona**: HR Professional with digital workflow expertise
- **Task**: Create fillable forms for onboarding and compliance
- **Documents**: 15 Acrobat tutorials and guides
- **Key Outputs**: Form creation, security features, integration workflows

### Collection 3: Vegetarian Corporate Catering
- **Challenge ID**: `round_1b_001`
- **Persona**: Professional Food Contractor for corporate events
- **Task**: Design vegetarian buffet menu for 150 people
- **Documents**: 9 cooking and meal planning guides
- **Key Outputs**: Large-scale recipes, dietary accommodations, cost efficiency

## 🔧 Technical Features

### Multi-Stage Analysis Pipeline
1. **Document Processing**: PyMuPDF-based text extraction with structure preservation
2. **Heading Classification**: Random Forest classifier for document hierarchy detection
3. **Relevance Analysis**: TF-IDF + keyword matching for persona-specific scoring
4. **Section Ranking**: Multi-factor importance scoring with content quality assessment
5. **Output Generation**: Structured JSON with metadata and traceability

### Performance Specifications
- ⏱️ **Processing Time**: < 60 seconds per collection (3-15 documents)
- 💾 **Memory Usage**: < 1GB RAM requirement
- 🖥️ **CPU Only**: No GPU dependencies
- 📦 **Model Size**: < 1GB total footprint
- 🔄 **Offline**: No internet access required during execution

### Intelligent Features
- **Persona-Aware Analysis**: Content relevance tailored to user expertise and role
- **Job-Specific Prioritization**: Task-driven section importance ranking
- **Adaptive Classification**: Self-training heading detection for diverse document formats
- **Quality Filtering**: Noise removal and meaningful content extraction
- **Multi-Modal Scoring**: Combines semantic similarity with keyword matching

## 📁 Input/Output Format

### Input Structure (`challenge1b_input.json`)
```json
{
  "challenge_info": {
    "challenge_id": "round_1b_XXX",
    "test_case_name": "specific_test_case"
  },
  "documents": [
    {"filename": "document.pdf", "title": "Document Title"}
  ],
  "persona": {
    "role": "Detailed persona description with expertise areas"
  },
  "job_to_be_done": {
    "task": "Specific, actionable task description"
  }
}
```

### Output Structure (`challenge1b_output.json`)
```json
{
  "metadata": {
    "input_documents": ["list of processed files"],
    "persona": "User persona description",
    "job_to_be_done": "Task description", 
    "processing_timestamp": "2024-07-28T14:30:25.123456",
    "processing_time_seconds": 45.67,
    "challenge_info": {"challenge_id": "round_1b_XXX"},
    "total_sections_found": 127,
    "top_sections_returned": 10
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Relevant Section Title",
      "page_number": 15,
      "importance_rank": 1,
      "importance_score": 0.8945
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf", 
      "section_title": "Section Title",
      "refined_text": "Cleaned and contextualized content...",
      "page_number": 15,
      "relevance_score": 0.9234
    }
  ]
}
```

## 🚀 Usage Examples

### Multi-Collection Processing
```bash
# Process all collections
python main.py --collections_dir Challenge_1b/

# Output: challenge1b_output.json in each collection directory
```

### Single Collection Processing  
```bash
# Process individual collection
python main.py \
  --input_dir "Challenge_1b/Collection 1/PDFs/" \
  --persona "Travel Planner specializing in group travel coordination..." \
  --job "Plan a comprehensive 4-day trip itinerary for 10 college friends..." \
  --output travel_analysis.json
```

### Docker Deployment
```bash
# Build container
docker build -t pdf-analyst .

# Setup collections
docker run --rm -v $(pwd):/app pdf-analyst python setup_collections.py

# Run analysis  
docker run --rm -v $(pwd):/app pdf-analyst python main.py --collections_dir Challenge_1b/
```

## 🧪 Testing & Validation

### Run Test Suite
```bash
# Comprehensive testing
python test_system.py

# Tests include:
# - Collections setup validation
# - Input JSON structure verification  
# - Processing functionality testing
# - Output format validation
# - Performance benchmarking
```

### Expected Test Output
```
🚀 Starting Challenge 1b Document Analysis System Test Suite
📅 Test run: 2024-07-28 14:30:25

🧪 Testing Collections Setup
✅ Collections setup completed successfully
✅ Challenge_1b/Collection 1 structure is correct
✅ Challenge_1b/Collection 2 structure is correct  
✅ Challenge_1b/Collection 3 structure is correct

📊 TEST SUMMARY
Collections Setup         ✅ PASS
Input Validation          ✅ PASS
Single Collection         ✅ PASS
All Collections           ✅ PASS

🎯 Overall Result: 4/4 tests passed
🎉 All tests passed successfully!
```

## 📚 Documentation

- **[approach_explanation.md](approach_explanation.md)**: Technical methodology and algorithms
- **[EXECUTION_INSTRUCTIONS.md](EXECUTION_INSTRUCTIONS.md)**: Detailed setup and deployment guide
- **Collection README files**: Specific PDF requirements for each collection
- **Code documentation**: Inline comments and docstrings throughout system

## 🔍 Sample Results Preview

### Travel Planning Collection Output
```json
{
  "extracted_sections": [
    {
      "document": "south_france_guide_1.pdf",
      "section_title": "Essential 4-Day Itinerary for Groups", 
      "importance_rank": 1,
      "importance_score": 0.8945
    },
    {
      "document": "cote_azur_attractions.pdf",
      "section_title": "Budget-Friendly Group Activities",
      "importance_rank": 2,
      "importance_score": 0.8721
    }
  ],
  "subsection_analysis": [
    {
      "refined_text": "For groups of 8-12 young travelers, the South of France offers an incredible mix of culture, beaches, and nightlife. Day 1 should focus on arrival in Nice, settling into budget accommodations, and exploring the Old Town..."
    }
  ]
}
```

## 🛠️ Dependencies

```txt
pandas==2.0.3
scikit-learn==1.3.0  
PyMuPDF==1.23.3
numpy==1.24.3
```

## 📋 System Requirements

- **Python**: 3.9+ 
- **RAM**: 1GB minimum, 2GB recommended
- **Storage**: 500MB for system + PDF files
- **CPU**: Multi-core recommended for faster processing
- **OS**: Linux, macOS, Windows (Docker compatible)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python test_system.py`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

## 📄 License

This project is part of the Challenge 1b competition submission. Please refer to competition guidelines for usage terms.

## 🆘 Support & Troubleshooting

### Common Issues

**No PDF files found**: Add required PDF files to each collection's `PDFs/` directory as specified in README files.

**Import errors**: Install dependencies with `pip install -r requirements.txt`

**Memory issues**: Process collections individually or reduce batch sizes for large documents.

**Permission errors**: Check file permissions or use appropriate Docker user mapping.

### Performance Optimization

- Use SSD storage for faster file I/O
- Allocate sufficient RAM (2GB+ recommended)
- Process collections sequentially for memory-constrained environments
- Monitor processing times to ensure < 60 second constraint compliance

### Debug Information
```bash
# Check system status
python -c "import fitz, pandas, sklearn; print('Dependencies OK')"

# Validate collection structure  
ls -la Challenge_1b/Collection*/

# Test single document processing
python main.py --input_dir test_data/ --persona "Test" --job "Test" --output debug.json
```

---

**Challenge 1b**: Multi-Collection PDF Analysis System  
**Version**: 1.0  
**Last Updated**: July 28, 2024