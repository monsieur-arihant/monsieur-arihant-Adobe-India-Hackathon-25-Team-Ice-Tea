#!/usr/bin/env python3
"""
Intelligent Document Analyst System
Theme: "Connect What Matters — For the User Who Matters"
"""

import fitz  # PyMuPDF
import pandas as pd
import numpy as np
import json
import os
import re
import string
from datetime import datetime
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
import argparse

class DocumentProcessor:
    """Handles PDF text extraction and preprocessing"""
    
    def __init__(self):
        self.sections_data = []
        
    def is_meaningful(self, text: str) -> bool:
        """Filter out meaningless text fragments"""
        text = text.strip()
        if not text or len(text) < 3:
            return False
        
        # Remove junk symbols
        allowed_chars = string.ascii_letters + string.digits + string.punctuation + ' '
        cleaned = ''.join(c for c in text if c in allowed_chars)
        
        # Check if mostly alphanumeric
        alpha_ratio = sum(1 for c in cleaned if c.isalnum()) / len(cleaned) if cleaned else 0
        return len(cleaned.strip()) >= 3 and alpha_ratio > 0.3
    
    def extract_text_with_structure(self, pdf_path: str) -> List[Dict]:
        """Extract text with structural information"""
        doc = fitz.open(pdf_path)
        sections = []
        
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block['type'] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if not self.is_meaningful(text):
                                continue
                                
                            sections.append({
                                "document": os.path.basename(pdf_path),
                                "page": page_num + 1,
                                "text": text,
                                "font_size": span["size"],
                                "font_name": span["font"],
                                "bold": "Bold" in span["font"],
                                "x0": span["bbox"][0],
                                "y0": span["bbox"][1],
                                "x1": span["bbox"][2],
                                "y1": span["bbox"][3],
                                "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
                                "length": len(text),
                            })
        
        doc.close()
        return sections

class HeadingClassifier:
    """Classifies text into heading levels and paragraphs"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.is_trained = False
    
    def create_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create rule-based labels for training"""
        mean_font = df["font_size"].mean()
        std_font = df["font_size"].std()
        
        def label_row(row):
            font = row["font_size"]
            bold = row["bold"]
            upper = row["uppercase_ratio"]
            length = row["length"]
            
            # Title: Large font, often bold, short
            if font >= mean_font + 2 * std_font and length < 100:
                return "TITLE"
            # H1: Large font, bold, moderate uppercase
            elif font >= mean_font + 1.5 * std_font and bold and upper > 0.3:
                return "H1"
            # H2: Medium-large font, may be bold
            elif font >= mean_font + 0.75 * std_font and (bold or upper > 0.5):
                return "H2"
            # H3: Slightly larger font or bold
            elif font >= mean_font + 0.25 * std_font and bold:
                return "H3"
            # Everything else is paragraph
            else:
                return "P"
        
        df["label"] = df.apply(label_row, axis=1)
        return df
    
    def train(self, df: pd.DataFrame):
        """Train the heading classifier"""
        df = self.create_labels(df)
        
        features = df[["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]].astype(float)
        labels = df["label"]
        
        self.model.fit(features, labels)
        self.is_trained = True
        
        return df
    
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict heading levels"""
        if not self.is_trained:
            df = self.train(df)
        
        features = df[["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]].astype(float)
        df["predicted_label"] = self.model.predict(features)
        
        return df

class RelevanceAnalyzer:
    """Analyzes document relevance to persona and job-to-be-done"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Simple keyword extraction using common patterns
        keywords = []
        
        # Extract technical terms (capitalized words)
        tech_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        keywords.extend(tech_terms)
        
        # Extract acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        keywords.extend(acronyms)
        
        return list(set(keywords))
    
    def calculate_relevance(self, sections_df: pd.DataFrame, persona: str, job: str) -> pd.DataFrame:
        """Calculate relevance scores for each section"""
        # Combine persona and job descriptions
        query_text = f"{persona} {job}"
        
        # Prepare text corpus
        documents = sections_df['text'].tolist() + [query_text]
        
        # Compute TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        
        # Calculate similarity with query (last document)
        query_vector = tfidf_matrix[-1]
        document_vectors = tfidf_matrix[:-1]
        
        similarities = cosine_similarity(document_vectors, query_vector).flatten()
        sections_df['relevance_score'] = similarities
        
        # Add keyword-based scoring
        persona_keywords = self.extract_keywords(persona)
        job_keywords = self.extract_keywords(job)
        all_keywords = persona_keywords + job_keywords
        
        def keyword_score(text):
            text_lower = text.lower()
            matches = sum(1 for kw in all_keywords if kw.lower() in text_lower)
            return matches / len(all_keywords) if all_keywords else 0
        
        sections_df['keyword_score'] = sections_df['text'].apply(keyword_score)
        
        # Combined score
        sections_df['combined_score'] = (
            0.7 * sections_df['relevance_score'] + 
            0.3 * sections_df['keyword_score']
        )
        
        return sections_df

class DocumentAnalyst:
    """Main system orchestrator"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.classifier = HeadingClassifier()
        self.analyzer = RelevanceAnalyzer()
    
    def group_into_sections(self, df: pd.DataFrame) -> List[Dict]:
        """Group text fragments into logical sections"""
        sections = []
        current_section = None
        
        # Sort by document, page, and position
        df_sorted = df.sort_values(['document', 'page', 'y0'])
        
        for _, row in df_sorted.iterrows():
            if row['predicted_label'] in ['TITLE', 'H1', 'H2', 'H3']:
                # Start new section
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    'document': row['document'],
                    'page': row['page'],
                    'section_title': row['text'],
                    'content': [],
                    'combined_score': row['combined_score'],
                    'heading_level': row['predicted_label']
                }
            elif current_section and row['predicted_label'] == 'P':
                # Add paragraph to current section
                current_section['content'].append({
                    'text': row['text'],
                    'page': row['page'],
                    'score': row['combined_score']
                })
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def rank_sections(self, sections: List[Dict], top_k: int = 10) -> List[Dict]:
        """Rank sections by importance"""
        # Calculate section scores
        for section in sections:
            if section['content']:
                content_scores = [item['score'] for item in section['content']]
                section['avg_content_score'] = np.mean(content_scores)
                section['max_content_score'] = np.max(content_scores)
                section['content_length'] = sum(len(item['text']) for item in section['content'])
            else:
                section['avg_content_score'] = 0
                section['max_content_score'] = 0
                section['content_length'] = 0
            
            # Final importance score
            section['importance_score'] = (
                0.4 * section['combined_score'] +
                0.3 * section['avg_content_score'] +
                0.2 * section['max_content_score'] +
                0.1 * min(section['content_length'] / 1000, 1.0)  # Normalize content length
            )
        
        # Sort by importance and return top-k
        sections_sorted = sorted(sections, key=lambda x: x['importance_score'], reverse=True)
        
        # Add ranking
        for i, section in enumerate(sections_sorted[:top_k]):
            section['importance_rank'] = i + 1
        
        return sections_sorted[:top_k]
    
    def analyze_documents(self, pdf_paths: List[str], persona: str, job: str) -> Dict[str, Any]:
        """Main analysis pipeline"""
        print("🔄 Extracting text from documents...")
        
        # Extract text from all documents
        all_sections = []
        for pdf_path in pdf_paths:
            sections = self.processor.extract_text_with_structure(pdf_path)
            all_sections.extend(sections)
        
        if not all_sections:
            raise ValueError("No meaningful text extracted from documents")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_sections)
        df['bold'] = df['bold'].astype(int)
        
        print("🔄 Classifying headings...")
        # Classify headings
        df = self.classifier.train(df)
        
        print("🔄 Analyzing relevance...")
        # Analyze relevance
        df = self.analyzer.calculate_relevance(df, persona, job)
        
        print("🔄 Grouping into sections...")
        # Group into sections
        sections = self.group_into_sections(df)
        
        print("🔄 Ranking sections...")
        # Rank sections
        top_sections = self.rank_sections(sections)
        
        # Prepare output
        output = {
            "metadata": {
                "input_documents": [os.path.basename(path) for path in pdf_paths],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat(),
                "total_sections_found": len(sections),
                "top_sections_returned": len(top_sections)
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }
        
        # Fill extracted sections
        for section in top_sections:
            output["extracted_sections"].append({
                "document": section['document'],
                "page_number": section['page'],
                "section_title": section['section_title'],
                "importance_rank": section['importance_rank'],
                "importance_score": round(section['importance_score'], 4)
            })
        
        # Fill subsection analysis
        for section in top_sections:
            for i, content_item in enumerate(section['content'][:3]):  # Top 3 paragraphs per section
                refined_text = content_item['text']
                if len(refined_text) > 500:
                    refined_text = refined_text[:500] + "..."
                
                output["subsection_analysis"].append({
                    "document": section['document'],
                    "section_title": section['section_title'],
                    "refined_text": refined_text,
                    "page_number": content_item['page'],
                    "relevance_score": round(content_item['score'], 4)
                })
        
        return output

def process_collection(collection_dir: str) -> bool:
    """Process a single collection directory"""
    # Look for input JSON file
    input_file = os.path.join(collection_dir, "challenge1b_input.json")
    if not os.path.exists(input_file):
        print(f"❌ No input file found in {collection_dir}")
        return False
    
    # Load input configuration
    with open(input_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Extract configuration
    persona = config.get("persona", {}).get("role", "")
    job = config.get("job_to_be_done", {}).get("task", "")
    
    # Find PDF directory
    pdf_dir = os.path.join(collection_dir, "PDFs")
    if not os.path.exists(pdf_dir):
        print(f"❌ No PDFs directory found in {collection_dir}")
        return False
    
    # Find PDF files
    pdf_files = []
    for file in os.listdir(pdf_dir):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(pdf_dir, file))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_dir}")
        return False
    
    print(f"📄 Processing collection: {os.path.basename(collection_dir)}")
    print(f"📄 Found {len(pdf_files)} PDF files")
    print(f"👤 Persona: {persona}")
    print(f"🎯 Job: {job}")
    
    # Initialize system
    analyst = DocumentAnalyst()
    
    try:
        # Analyze documents
        start_time = datetime.now()
        result = analyst.analyze_documents(pdf_files, persona, job)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        result["metadata"]["processing_time_seconds"] = round(processing_time, 2)
        
        # Add challenge info if available
        if "challenge_info" in config:
            result["metadata"]["challenge_info"] = config["challenge_info"]
        
        # Save output
        output_file = os.path.join(collection_dir, "challenge1b_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis complete in {processing_time:.2f} seconds")
        print(f"📊 Found {len(result['extracted_sections'])} relevant sections")
        print(f"💾 Output saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {collection_dir}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Multi-Collection PDF Analysis System")
    parser.add_argument("--input_dir", help="Directory containing PDF files (single collection mode)")
    parser.add_argument("--collections_dir", help="Directory containing multiple collection subdirectories")
    parser.add_argument("--persona", help="Persona description (single collection mode)")
    parser.add_argument("--job", help="Job to be done (single collection mode)")
    parser.add_argument("--output", default="output.json", help="Output JSON file (single collection mode)")
    
    args = parser.parse_args()
    
    if args.collections_dir:
        # Multi-collection mode
        print("🚀 Running Multi-Collection Analysis")
        
        collections = []
        for item in os.listdir(args.collections_dir):
            item_path = os.path.join(args.collections_dir, item)
            if os.path.isdir(item_path) and item.startswith("Collection"):
                collections.append(item_path)
        
        if not collections:
            print("❌ No collection directories found")
            return
        
        print(f"📁 Found {len(collections)} collections")
        
        success_count = 0
        for collection_dir in sorted(collections):
            print(f"\n{'='*50}")
            if process_collection(collection_dir):
                success_count += 1
        
        print(f"\n🎉 Successfully processed {success_count}/{len(collections)} collections")
        
    elif args.input_dir and args.persona and args.job:
        # Single collection mode (legacy)
        pdf_files = []
        for file in os.listdir(args.input_dir):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(args.input_dir, file))
        
        if not pdf_files:
            print("❌ No PDF files found in input directory")
            return
        
        print(f"📄 Found {len(pdf_files)} PDF files")
        print(f"👤 Persona: {args.persona}")
        print(f"🎯 Job: {args.job}")
        
        analyst = DocumentAnalyst()
        
        try:
            start_time = datetime.now()
            result = analyst.analyze_documents(pdf_files, args.persona, args.job)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            result["metadata"]["processing_time_seconds"] = round(processing_time, 2)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Analysis complete in {processing_time:.2f} seconds")
            print(f"📊 Found {len(result['extracted_sections'])} relevant sections")
            print(f"💾 Output saved to: {args.output}")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            raise
    else:
        parser.print_help()

if __name__ == "__main__":
    main()