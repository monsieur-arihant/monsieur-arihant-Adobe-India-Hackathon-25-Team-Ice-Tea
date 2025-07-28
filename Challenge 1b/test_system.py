#!/usr/bin/env python3
"""
Test script for the Challenge 1b Document Analysis System
"""

import os
import json
import subprocess
import time
from datetime import datetime

def test_collections_setup():
    """Test the collections setup process"""
    print("🧪 Testing Collections Setup")
    
    # Run setup script
    result = subprocess.run(["python", "setup_collections.py"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Collections setup completed successfully")
        
        # Check if directories were created
        expected_dirs = [
            "Challenge_1b/Collection 1",
            "Challenge_1b/Collection 2", 
            "Challenge_1b/Collection 3"
        ]
        
        for dir_path in expected_dirs:
            if os.path.exists(dir_path):
                # Check for required files
                input_file = os.path.join(dir_path, "challenge1b_input.json")
                pdfs_dir = os.path.join(dir_path, "PDFs")
                
                if os.path.exists(input_file) and os.path.exists(pdfs_dir):
                    print(f"✅ {dir_path} structure is correct")
                else:
                    print(f"❌ {dir_path} missing required files")
            else:
                print(f"❌ {dir_path} not created")
        
        return True
    else:
        print("❌ Collections setup failed")
        print(f"Error: {result.stderr}")
        return False

def test_single_collection():
    """Test processing a single collection with sample data"""
    print("\n🧪 Testing Single Collection Processing")
    
    collection_dir = "Challenge_1b/Collection 1"
    
    if not os.path.exists(collection_dir):
        print("❌ Collection 1 directory not found. Run setup first.")
        return False
    
    # Check if PDFs exist
    pdfs_dir = os.path.join(collection_dir, "PDFs")
    pdf_files = [f for f in os.listdir(pdfs_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("⚠️  No PDF files found in Collection 1/PDFs/")
        print("📝 Add PDF files to test processing functionality")
        return True  # Not a failure, just no data to process
    
    print(f"📄 Found {len(pdf_files)} PDF files in Collection 1")
    
    # Process the collection
    cmd = ["python", "main.py", "--collections_dir", "Challenge_1b/"]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    processing_time = end_time - start_time
    print(f"⏱️  Processing time: {processing_time:.2f} seconds")
    
    if result.returncode == 0:
        print("✅ Collection processing completed successfully")
        
        # Check if output file was created
        output_file = os.path.join(collection_dir, "challenge1b_output.json")
        if os.path.exists(output_file):
            print("✅ Output file created successfully")
            
            # Validate output structure
            return validate_output_format(output_file)
        else:
            print("❌ Output file not created")
            return False
    else:
        print("❌ Collection processing failed")
        print(f"Error: {result.stderr}")
        return False

def test_all_collections():
    """Test processing all collections"""
    print("\n🧪 Testing All Collections Processing")
    
    if not os.path.exists("Challenge_1b"):
        print("❌ Challenge_1b directory not found. Run setup first.")
        return False
    
    # Count collections with PDFs
    collections_with_pdfs = 0
    for i in range(1, 4):
        collection_dir = f"Challenge_1b/Collection {i}"
        if os.path.exists(collection_dir):
            pdfs_dir = os.path.join(collection_dir, "PDFs")
            if os.path.exists(pdfs_dir):
                pdf_files = [f for f in os.listdir(pdfs_dir) if f.lower().endswith('.pdf')]
                if pdf_files:
                    collections_with_pdfs += 1
                    print(f"📄 Collection {i}: {len(pdf_files)} PDF files")
    
    if collections_with_pdfs == 0:
        print("⚠️  No PDF files found in any collection")
        print("📝 Add PDF files to test processing functionality")
        return True
    
    print(f"🎯 Testing {collections_with_pdfs} collections with PDF data")
    
    # Process all collections
    cmd = ["python", "main.py", "--collections_dir", "Challenge_1b/"]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    processing_time = end_time - start_time
    print(f"⏱️  Total processing time: {processing_time:.2f} seconds")
    
    if result.returncode == 0:
        print("✅ All collections processed successfully")
        
        # Check output files
        success_count = 0
        for i in range(1, 4):
            output_file = f"Challenge_1b/Collection {i}/challenge1b_output.json"
            if os.path.exists(output_file):
                if validate_output_format(output_file):
                    success_count += 1
                    print(f"✅ Collection {i} output validated")
                else:
                    print(f"❌ Collection {i} output validation failed")
        
        print(f"📊 Successfully processed {success_count}/{collections_with_pdfs} collections")
        return success_count == collections_with_pdfs
    else:
        print("❌ Collections processing failed")
        print(f"Error: {result.stderr}")
        return False

def validate_output_format(output_file: str) -> bool:
    """Validate Challenge 1b output JSON format"""
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        # Check required top-level keys
        required_keys = ["metadata", "extracted_sections", "subsection_analysis"]
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Check metadata structure
        metadata_keys = ["input_documents", "persona", "job_to_be_done", "processing_timestamp"]
        for key in metadata_keys:
            if key not in data["metadata"]:
                print(f"❌ Missing metadata key: {key}")
                return False
        
        # Check for challenge_info (specific to Challenge 1b)
        if "challenge_info" in data["metadata"]:
            challenge_keys = ["challenge_id", "test_case_name"]
            for key in challenge_keys:
                if key not in data["metadata"]["challenge_info"]:
                    print(f"❌ Missing challenge_info key: {key}")
                    return False
        
        # Check extracted sections structure
        if data["extracted_sections"]:
            section_keys = ["document", "page_number", "section_title", "importance_rank"]
            for key in section_keys:
                if key not in data["extracted_sections"][0]:
                    print(f"❌ Missing extracted section key: {key}")
                    return False
        
        # Check subsection analysis structure  
        if data["subsection_analysis"]:
            subsection_keys = ["document", "refined_text", "page_number"]
            for key in subsection_keys:
                if key not in data["subsection_analysis"][0]:
                    print(f"❌ Missing subsection analysis key: {key}")
                    return False
        
        # Check processing time constraint (should be < 60 seconds)
        if "processing_time_seconds" in data["metadata"]:
            processing_time = data["metadata"]["processing_time_seconds"]
            if processing_time > 60:
                print(f"⚠️  Processing time {processing_time}s exceeds 60s constraint")
        
        print(f"✅ Output format validation passed for {os.path.basename(output_file)}")
        return True
        
    except Exception as e:
        print(f"❌ Output validation failed: {e}")
        return False

def test_input_validation():
    """Test input JSON validation"""
    print("\n🧪 Testing Input JSON Validation")
    
    test_files = [
        "Challenge_1b/Collection 1/challenge1b_input.json",
        "Challenge_1b/Collection 2/challenge1b_input.json", 
        "Challenge_1b/Collection 3/challenge1b_input.json"
    ]
    
    valid_count = 0
    for input_file in test_files:
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r') as f:
                    data = json.load(f)
                
                # Check required structure
                required_keys = ["challenge_info", "documents", "persona", "job_to_be_done"]
                if all(key in data for key in required_keys):
                    print(f"✅ {os.path.basename(input_file)} structure valid")
                    valid_count += 1
                else:
                    print(f"❌ {os.path.basename(input_file)} missing required keys")
                    
            except Exception as e:
                print(f"❌ {os.path.basename(input_file)} validation failed: {e}")
        else:
            print(f"❌ {input_file} not found")
    
    print(f"📊 Input validation: {valid_count}/{len(test_files)} files valid")
    return valid_count == len(test_files)

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n📋 Generating Test Report")
    
    report = {
        "test_run": datetime.now().isoformat(),
        "system_info": {
            "python_version": subprocess.run(["python", "--version"], capture_output=True, text=True).stdout.strip(),
            "platform": os.name
        },
        "test_results": {},
        "performance_metrics": {},
        "file_status": {}
    }
    
    # Check file structure
    if os.path.exists("Challenge_1b"):
        for i in range(1, 4):
            collection_dir = f"Challenge_1b/Collection {i}"
            if os.path.exists(collection_dir):
                pdfs_dir = os.path.join(collection_dir, "PDFs")
                pdf_count = len([f for f in os.listdir(pdfs_dir) if f.lower().endswith('.pdf')]) if os.path.exists(pdfs_dir) else 0
                
                output_file = os.path.join(collection_dir, "challenge1b_output.json")
                has_output = os.path.exists(output_file)
                
                report["file_status"][f"Collection {i}"] = {
                    "pdf_files": pdf_count,
                    "has_output": has_output,
                    "output_size": os.path.getsize(output_file) if has_output else 0
                }
    
    # Save report
    with open("test_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print("💾 Test report saved to: test_report.json")

def main():
    print("🚀 Starting Challenge 1b Document Analysis System Test Suite")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test results tracking
    test_results = []
    
    # Test 1: Collections Setup
    print(f"\n{'='*60}")
    try:
        result = test_collections_setup()
        test_results.append(("Collections Setup", result))
    except Exception as e:
        print(f"❌ Collections Setup error: {e}")
        test_results.append(("Collections Setup", False))
    
    # Test 2: Input Validation
    print(f"\n{'='*60}")
    try:
        result = test_input_validation()
        test_results.append(("Input Validation", result))
    except Exception as e:
        print(f"❌ Input Validation error: {e}")
        test_results.append(("Input Validation", False))
    
    # Test 3: Single Collection Processing
    print(f"\n{'='*60}")
    try:
        result = test_single_collection()
        test_results.append(("Single Collection", result))
    except Exception as e:
        print(f"❌ Single Collection error: {e}")
        test_results.append(("Single Collection", False))
    
    # Test 4: All Collections Processing
    print(f"\n{'='*60}")
    try:
        result = test_all_collections()
        test_results.append(("All Collections", result))
    except Exception as e:
        print(f"❌ All Collections error: {e}")
        test_results.append(("All Collections", False))
    
    # Test Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed successfully!")
        print("\n💡 Next Steps:")
        print("1. Add PDF files to Challenge_1b/Collection X/PDFs/ directories")
        print("2. Run: python main.py --collections_dir Challenge_1b/")
        print("3. Check challenge1b_output.json files in each collection")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check file permissions in the working directory")
        print("3. Verify Python version is 3.9+ compatible")
    
    # Generate detailed report
    try:
        generate_test_report()
    except Exception as e:
        print(f"⚠️  Could not generate test report: {e}")
    
    # Performance summary
    print(f"\n⚡ Performance Notes:")
    print("- Processing time should be < 60 seconds per collection")
    print("- Memory usage should stay under 1GB")
    print("- CPU-only processing (no GPU required)")
    print("- Model size constraint: < 1GB total")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)#!/usr/bin/env python3
"""
Test script for the Document Analysis System
"""

import os
import json
import subprocess
import time
from datetime import datetime

def test_case_1():
    """Test Case 1: Academic Research"""
    print("🧪 Running Test Case 1: Academic Research")
    
    persona = "PhD Researcher in Computational Biology with expertise in machine learning applications for drug discovery, molecular modeling, and biomedical data analysis"
    job = "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks for Graph Neural Networks in drug discovery applications"
    
    cmd = [
        "python", "main.py",
        "--input_dir", "test_cases/case1_academic",
        "--persona", persona,
        "--job", job,
        "--output", "output/case1_output.json"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️  Processing time: {end_time - start_time:.2f} seconds")
    print(f"📤 Return code: {result.returncode}")
    
    if result.returncode == 0:
        print("✅ Test Case 1 completed successfully")
        with open("output/case1_output.json", 'r') as f:
            output = json.load(f)
            print(f"📊 Found {len(output['extracted_sections'])} relevant sections")
    else:
        print("❌ Test Case 1 failed")
        print(f"Error: {result.stderr}")
    
    return result.returncode == 0

def test_case_2():
    """Test Case 2: Business Analysis"""
    print("\n🧪 Running Test Case 2: Business Analysis")
    
    persona = "Senior Investment Analyst specializing in technology sector analysis, financial modeling, and competitive intelligence with 8+ years experience in equity research"
    job = "Analyze revenue trends, R&D investments, and market positioning strategies across competing technology companies for investment decision making"
    
    cmd = [
        "python", "main.py",
        "--input_dir", "test_cases/case2_business",
        "--persona", persona,
        "--job", job,
        "--output", "output/case2_output.json"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️  Processing time: {end_time - start_time:.2f} seconds")
    print(f"📤 Return code: {result.returncode}")
    
    if result.returncode == 0:
        print("✅ Test Case 2 completed successfully")
        with open("output/case2_output.json", 'r') as f:
            output = json.load(f)
            print(f"📊 Found {len(output['extracted_sections'])} relevant sections")
    else:
        print("❌ Test Case 2 failed")
        print(f"Error: {result.stderr}")
    
    return result.returncode == 0

def test_case_3():
    """Test Case 3: Educational Content"""
    print("\n🧪 Running Test Case 3: Educational Content")
    
    persona = "Undergraduate Chemistry Student in third year focusing on organic chemistry, preparing for comprehensive exams with strong foundation in general chemistry"
    job = "Identify key concepts and mechanisms for exam preparation on reaction kinetics, including rate laws, activation energy, and catalysis mechanisms"
    
    cmd = [
        "python", "main.py",
        "--input_dir", "test_cases/case3_education",
        "--persona", persona,
        "--job", job,
        "--output", "output/case3_output.json"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️  Processing time: {end_time - start_time:.2f} seconds")
    print(f"📤 Return code: {result.returncode}")
    
    if result.returncode == 0:
        print("✅ Test Case 3 completed successfully")
        with open("output/case3_output.json", 'r') as f:
            output = json.load(f)
            print(f"📊 Found {len(output['extracted_sections'])} relevant sections")
    else:
        print("❌ Test Case 3 failed")
        print(f"Error: {result.stderr}")
    
    return result.returncode == 0

def create_sample_data():
    """Create sample test directories and placeholder files"""
    test_cases = [
        "test_cases/case1_academic",
        "test_cases/case2_business", 
        "test_cases/case3_education",
        "output"
    ]
    
    for case_dir in test_cases:
        os.makedirs(case_dir, exist_ok=True)
    
    # Create README files explaining how to add PDFs
    readme_content = {
        "case1_academic": "Add 3-5 research papers related to Graph Neural Networks and drug discovery in PDF format to this directory.",
        "case2_business": "Add 2-4 annual reports or financial documents from technology companies in PDF format to this directory.",
        "case3_education": "Add 3-5 chemistry textbook chapters or educational materials about reaction kinetics in PDF format to this directory."
    }
    
    for case, content in readme_content.items():
        readme_path = f"test_cases/{case}/README.txt"
        with open(readme_path, 'w') as f:
            f.write(content)
    
    print("📁 Created test case directories with README files")

def validate_output_format(output_file: str) -> bool:
    """Validate output JSON format"""
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        # Check required top-level keys
        required_keys = ["metadata", "extracted_sections", "subsection_analysis"]
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Check metadata structure
        metadata_keys = ["input_documents", "persona", "job_to_be_done", "processing_timestamp"]
        for key in metadata_keys:
            if key not in data["metadata"]:
                print(f"❌ Missing metadata key: {key}")
                return False
        
        # Check extracted sections structure
        if data["extracted_sections"]:
            section_keys = ["document", "page_number", "section_title", "importance_rank"]
            for key in section_keys:
                if key not in data["extracted_sections"][0]:
                    print(f"❌ Missing extracted section key: {key}")
                    return False
        
        # Check subsection analysis structure
        if data["subsection_analysis"]:
            subsection_keys = ["document", "refined_text", "page_number"]
            for key in subsection_keys:
                if key not in data["subsection_analysis"][0]:
                    print(f"❌ Missing subsection analysis key: {key}")
                    return False
        
        print("✅ Output format validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Output validation failed: {e}")
        return False

def main():
    print("🚀 Starting Document Analysis System Test Suite")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create sample directories
    create_sample_data()
    
    # Check if we have actual PDF files to test with
    has_pdfs = False
    for case_dir in ["test_cases/case1_academic", "test_cases/case2_business", "test_cases/case3_education"]:
        pdf_files = [f for f in os.listdir(case_dir) if f.lower().endswith('.pdf')]
        if pdf_files:
            has_pdfs = True
            break
    
    if not has_pdfs:
        print("⚠️  No PDF files found in test case directories.")
        print("📝 Please add PDF files to the test_cases subdirectories before running tests.")
        print("💡 Check the README.txt files in each test case directory for guidance.")
        return
    
    # Run test cases
    results = []
    
    try:
        results.append(test_case_1())
    except Exception as e:
        print(f"❌ Test Case 1 error: {e}")
        results.append(False)
    
    try:    
        results.append(test_case_2())
    except Exception as e:
        print(f"❌ Test Case 2 error: {e}")
        results.append(False)
    
    try:
        results.append(test_case_3())
    except Exception as e:
        print(f"❌ Test Case 3 error: {e}")
        results.append(False)
    
    # Validate outputs
    output_files = [
        "output/case1_output.json",
        "output/case2_output.json", 
        "output/case3_output.json"
    ]
    
    for i, output_file in enumerate(output_files):
        if os.path.exists(output_file) and results[i]:
            validate_output_format(output_file)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} test cases passed")
    
    if passed == total:
        print("🎉 All tests passed successfully!")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()