#!/usr/bin/env python3
"""
Setup script to create the complete Challenge 1b directory structure
"""

import os
import json
import shutil

def create_collection_structure():
    """Create the Challenge 1b directory structure"""
    
    # Base directory
    base_dir = "Challenge_1b"
    os.makedirs(base_dir, exist_ok=True)
    
    # Collection definitions
    collections = {
        "Collection 1": {
            "challenge_id": "round_1b_002",
            "test_case_name": "travel_planning_south_france",
            "persona": "Travel Planner specializing in group travel coordination with expertise in European destinations, budget management, and activity planning for young adults",
            "task": "Plan a comprehensive 4-day trip itinerary for 10 college friends visiting South of France, including accommodations, activities, dining, and transportation recommendations within a student-friendly budget",
            "pdfs": [
                "south_france_guide_1.pdf",
                "provence_travel_guide.pdf", 
                "cote_azur_attractions.pdf",
                "french_riviera_activities.pdf",
                "marseille_city_guide.pdf",
                "nice_travel_tips.pdf",
                "south_france_food_wine.pdf"
            ]
        },
        "Collection 2": {
            "challenge_id": "round_1b_003",
            "test_case_name": "adobe_acrobat_hr_forms", 
            "persona": "HR Professional responsible for employee onboarding, compliance documentation, and digital workflow management with intermediate technical skills",
            "task": "Create and manage comprehensive fillable PDF forms for employee onboarding, performance reviews, and compliance documentation that are secure, accessible, and integrate with existing HR systems",
            "pdfs": [
                "acrobat_basics_tutorial.pdf",
                "creating_fillable_forms.pdf",
                "form_field_properties.pdf",
                "digital_signatures_guide.pdf",
                "pdf_optimization.pdf",
                "acrobat_collaboration.pdf",
                "accessibility_compliance.pdf",
                "batch_processing.pdf",
                "mobile_acrobat.pdf",
                "integration_workflows.pdf",
                "troubleshooting_guide.pdf",
                "advanced_editing.pdf",
                "document_security.pdf",
                "ai_features_acrobat.pdf",
                "compliance_standards.pdf"
            ]
        },
        "Collection 3": {
            "challenge_id": "round_1b_001",
            "test_case_name": "vegetarian_corporate_catering",
            "persona": "Professional Food Contractor specializing in corporate catering with expertise in large-scale meal preparation, dietary accommodations, and cost-effective menu planning",
            "task": "Design and prepare a comprehensive vegetarian buffet-style dinner menu for a corporate gathering of 150 people, ensuring variety, nutritional balance, dietary accommodation, and cost efficiency while maintaining professional presentation standards",
            "pdfs": [
                "vegetarian_cooking_basics.pdf",
                "buffet_planning_guide.pdf",
                "corporate_catering_handbook.pdf",
                "plant_based_proteins.pdf",
                "seasonal_vegetarian_menus.pdf",
                "dietary_restrictions_guide.pdf",
                "large_batch_cooking.pdf",
                "food_safety_standards.pdf",
                "cost_effective_vegetarian.pdf"
            ]
        }
    }
    
    for collection_name, config in collections.items():
        # Create collection directory
        collection_dir = os.path.join(base_dir, collection_name)
        os.makedirs(collection_dir, exist_ok=True)
        
        # Create PDFs subdirectory
        pdfs_dir = os.path.join(collection_dir, "PDFs")
        os.makedirs(pdfs_dir, exist_ok=True)
        
        # Create input JSON
        input_data = {
            "challenge_info": {
                "challenge_id": config["challenge_id"],
                "test_case_name": config["test_case_name"]
            },
            "documents": [
                {
                    "filename": pdf,
                    "title": pdf.replace('_', ' ').replace('.pdf', '').title()
                }
                for pdf in config["pdfs"]
            ],
            "persona": {
                "role": config["persona"]
            },
            "job_to_be_done": {
                "task": config["task"]
            }
        }
        
        input_file = os.path.join(collection_dir, "challenge1b_input.json")
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(input_data, f, indent=2, ensure_ascii=False)
        
        # Create README for PDFs directory
        readme_content = f"""# {collection_name} - PDF Documents

## Collection: {config['test_case_name']}
**Challenge ID**: {config['challenge_id']}

**Persona**: {config['persona']}

**Task**: {config['task']}

## Required PDF Files:
"""
        for pdf in config["pdfs"]:
            readme_content += f"- {pdf}\n"
        
        readme_content += f"""
## Instructions:
1. Add the {len(config['pdfs'])} PDF files listed above to this directory
2. Ensure filenames match exactly as specified
3. Run the analysis using: `python main.py --collections_dir Challenge_1b/`

## Expected Output:
- challenge1b_output.json will be generated in the collection root directory
- Contains extracted sections ranked by importance for the specific persona and task
"""
        
        readme_file = os.path.join(pdfs_dir, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ Created {collection_name}")
        print(f"   📁 Directory: {collection_dir}")
        print(f"   📄 Input config: challenge1b_input.json")
        print(f"   📚 PDFs needed: {len(config['pdfs'])} files")
    
    # Create main README
    main_readme = f"""# Challenge 1b: Multi-Collection PDF Analysis

## Overview
Advanced PDF analysis solution that processes multiple document collections and extracts relevant content based on specific personas and use cases.

## Project Structure
```
Challenge_1b/
├── Collection 1/                    # Travel Planning
│   ├── PDFs/                       # South of France guides  
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results (generated)
├── Collection 2/                    # Adobe Acrobat Learning
│   ├── PDFs/                       # Acrobat tutorials
│   ├── challenge1b_input.json      # Input configuration  
│   └── challenge1b_output.json     # Analysis results (generated)
├── Collection 3/                    # Recipe Collection
│   ├── PDFs/                       # Cooking guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results (generated)
└── README.md                       # This file
```

## Collections Summary

### Collection 1: Travel Planning South France
- **Challenge ID**: round_1b_002
- **Persona**: Travel Planner  
- **Task**: Plan 4-day trip for 10 college friends
- **Documents**: 7 travel guides

### Collection 2: Adobe Acrobat HR Forms  
- **Challenge ID**: round_1b_003
- **Persona**: HR Professional
- **Task**: Create fillable forms for onboarding and compliance
- **Documents**: 15 Acrobat guides

### Collection 3: Vegetarian Corporate Catering
- **Challenge ID**: round_1b_001  
- **Persona**: Food Contractor
- **Task**: Prepare vegetarian buffet menu for corporate gathering
- **Documents**: 9 cooking guides

## Usage Instructions

### 1. Setup PDF Files
Add the required PDF files to each collection's `PDFs/` directory as specified in the README files.

### 2. Run Analysis
```bash
# Process all collections
python main.py --collections_dir Challenge_1b/

# Process single collection (legacy mode)
python main.py --input_dir "Challenge_1b/Collection 1/PDFs/" --persona "Travel Planner..." --job "Plan a 4-day trip..." --output results.json
```

### 3. Review Results
Each collection will generate a `challenge1b_output.json` file with:
- Metadata about processing
- Extracted sections ranked by importance  
- Subsection analysis with refined content

## Output Format

### Input JSON Structure
```json
{{
  "challenge_info": {{
    "challenge_id": "round_1b_XXX",
    "test_case_name": "specific_test_case"
  }},
  "documents": [{{"filename": "doc.pdf", "title": "Title"}}],
  "persona": {{"role": "User Persona"}},
  "job_to_be_done": {{"task": "Task description"}}
}}
```

### Output JSON Structure  
```json
{{
  "metadata": {{
    "input_documents": ["list"],
    "persona": "User Persona", 
    "job_to_be_done": "Task description",
    "processing_timestamp": "ISO timestamp",
    "challenge_info": {{"challenge_id": "round_1b_XXX"}}
  }},
  "extracted_sections": [
    {{
      "document": "source.pdf",
      "section_title": "Title",
      "page_number": 1, 
      "importance_rank": 1
    }}
  ],
  "subsection_analysis": [
    {{
      "document": "source.pdf",
      "refined_text": "Content",
      "page_number": 1
    }}
  ]
}}
```

## Key Features
- **Persona-Based Analysis**: Content extraction tailored to specific user types
- **Importance Ranking**: Prioritizes content based on relevance
- **Multi-Collection Processing**: Handles diverse document collections
- **Structured Output**: Comprehensive JSON analysis with metadata

## Requirements
- Python 3.9+
- PyMuPDF (fitz)
- pandas
- scikit-learn
- numpy

Created: {base_dir} with {len(collections)} collections ready for PDF processing.
"""
    
    main_readme_file = os.path.join(base_dir, "README.md")
    with open(main_readme_file, 'w', encoding='utf-8') as f:
        f.write(main_readme)
    
    print(f"\n🎉 Challenge 1b structure created successfully!")
    print(f"📁 Base directory: {base_dir}")
    print(f"📋 Collections: {len(collections)}")
    print(f"📚 Total PDFs needed: {sum(len(config['pdfs']) for config in collections.values())}")
    print(f"\n📖 Next steps:")
    print(f"1. Add PDF files to each collection's PDFs/ directory")
    print(f"2. Run: python main.py --collections_dir {base_dir}/")

def main():
    create_collection_structure()

if __name__ == "__main__":
    main()