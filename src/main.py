import fitz, string, requests, os, re, pandas as pd, numpy as np, json
from sklearn.ensemble import RandomForestClassifier
from collections import Counter

os.makedirs("pdf_dataset", exist_ok=True)

# Download PDFs with size check
urls = ["https://arxiv.org/pdf/1706.03762.pdf", "https://arxiv.org/pdf/1605.08294.pdf", 
        "https://arxiv.org/pdf/1802.05365.pdf", "https://arxiv.org/pdf/1409.0473.pdf",
        "https://arxiv.org/pdf/1512.03385.pdf", "https://arxiv.org/pdf/1506.01497.pdf"]

for i, url in enumerate(urls, 1):
    try:
        r = requests.get(url, timeout=30, stream=True)
        if int(r.headers.get('content-length', 0)) > 48*1024*1024: continue
        content = r.content
        if len(content) > 48*1024*1024: continue
        with open(f"pdf_dataset/sample_{i}.pdf", "wb") as f: f.write(content)
        print(f"Downloaded sample_{i}.pdf")
    except: pass

def is_valid(text):
    text = text.strip()
    if not text or len(text) <= 1: return False
    if re.fullmatch(r"[^\w\s]+", text): return False
    if re.match(r".*\.{3,}\s*\d+$|^[\d\s.()ivxlcdm]{1,6}$|^[.\-_]{3,}$", text): return False
    return len(set(text.replace(' ', ''))) > 2 or len(text) >= 10

def is_watermark(span, ph, pw):
    y, x, fs = span["bbox"][1], span["bbox"][0], span["size"]
    return (span.get("alpha", 1) < 0.5 or fs > 50 or 
            y < 0.05*ph or y > 0.95*ph or x < 0.05*pw or x > 0.95*pw)

def is_toc(text, fs, mean_fs):
    return (re.search(r"\.{2,}\s*\d+\s*$", text) or 
            re.match(r"^\d+(\.\d+)*\s+[A-Za-z]", text) and fs < mean_fs)

def process_pdf(filename):
    doc = fitz.open(f"pdf_dataset/{filename}")
    all_items, data = [], []
    
    # First pass: collect all text for stats
    for page in doc:
        ph, pw = page.rect.height, page.rect.width
        for block in page.get_text("dict")["blocks"]:
            if block['type'] != 0: continue
            for line in block["lines"]:
                if not line["spans"]: continue
                text, bbox, fs, fn, bold = "", None, 0, "", False
                for span in line["spans"]:
                    if is_watermark(span, ph, pw) or not span["text"].strip(): continue
                    if bbox is None:
                        text, bbox, fs, fn = span["text"].strip(), span["bbox"], span["size"], span["font"]
                        bold = "Bold" in fn
                    elif abs(span["bbox"][1] - bbox[1]) < 3:
                        text += " " + span["text"].strip()
                        bbox = (min(bbox[0], span["bbox"][0]), bbox[1], 
                               max(bbox[2], span["bbox"][2]), bbox[3])
                        if span["size"] > fs: fs, fn, bold = span["size"], span["font"], "Bold" in span["font"]
                if text and is_valid(text):
                    all_items.append({"text": text, "bbox": bbox, "font_size": fs, "font_name": fn, "bold": bold})
    
    if not all_items: return []
    
    # Calculate font stats
    fonts = [item["font_size"] for item in all_items]
    mean_fs, std_fs = np.mean(fonts), np.std(fonts)
    mode_fs = Counter([round(f, 1) for f in fonts]).most_common(1)[0][0]
    
    # Second pass: label and collect data
    for page_num, page in enumerate(doc):
        ph = page.rect.height
        for block in page.get_text("dict")["blocks"]:
            if block['type'] != 0: continue
            for line in block["lines"]:
                if not line["spans"]: continue
                text, bbox, fs, fn, bold = "", None, 0, "", False
                for span in line["spans"]:
                    if is_watermark(span, ph, page.rect.width) or not span["text"].strip(): continue
                    if bbox is None:
                        text, bbox, fs, fn = span["text"].strip(), span["bbox"], span["size"], span["font"]
                        bold = "Bold" in fn
                    elif abs(span["bbox"][1] - bbox[1]) < 3:
                        text += " " + span["text"].strip()
                        if span["size"] > fs: fs, fn, bold = span["size"], span["font"], "Bold" in span["font"]
                
                if not text or not is_valid(text) or is_toc(text, fs, mean_fs): continue
                
                # Enhanced labeling
                t = text.strip()
                ratio = fs / mean_fs
                pos_ratio = bbox[1] / ph
                upper_ratio = sum(1 for c in t if c.isupper()) / len(t)
                
                if re.match(r"^\d+\.\d+\.\d+\s+[A-Z]", t): label = "H3"
                elif re.match(r"^\d+\.\d+\s+[A-Z]", t): label = "H2"
                elif re.match(r"^\d+\s+[A-Z]", t): label = "H1"
                elif ratio >= 1.5 and (pos_ratio < 0.3 or page_num < 3) and bold: label = "TITLE"
                elif ratio >= 1.3 and bold: label = "H1"
                elif ratio >= 1.15 and bold: label = "H2"
                elif ratio >= 1.05 and (bold or fs > mean_fs + 0.5): label = "H3"
                elif bold and len(t) < 100 and pos_ratio < 0.8: label = "H3"
                elif re.match(r"^(abstract|introduction|conclusion|references)$", t.lower()): 
                    label = "H1" if ratio >= 1.1 or bold else "H2"
                else: label = "P"
                
                data.append({
                    "filename": filename, "page": page_num + 1, "text": text, "font_size": fs,
                    "font_name": fn, "bold": bold, "x0": bbox[0], "y0": bbox[1],
                    "uppercase_ratio": upper_ratio, "length": len(text), "label": label
                })
    
    doc.close()
    return data

# Process all PDFs
data = []
for f in os.listdir("pdf_dataset"):
    if f.endswith(".pdf"):
        print(f"Processing: {f}")
        data.extend(process_pdf(f))

if data:
    df = pd.DataFrame(data)
    df.to_csv("pdf_dataset/heading_labels_enhanced.csv", index=False)
    print(f"Dataset saved: {len(df)} entries, Labels: {dict(df['label'].value_counts())}")
    
    # Train model
    df["bold"] = df["bold"].astype(int)
    features = ["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(df[features], df["label"])
    print("Model trained successfully.")

def predict_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_items, data = [], []
    
    # Collect all for stats
    for page in doc:
        ph, pw = page.rect.height, page.rect.width
        for block in page.get_text("dict")["blocks"]:
            if block['type'] != 0: continue
            for line in block["lines"]:
                if not line["spans"]: continue
                text, bbox, fs, fn, bold = "", None, 0, "", False
                for span in line["spans"]:
                    if is_watermark(span, ph, pw) or not span["text"].strip(): continue
                    if bbox is None:
                        text, bbox, fs, fn = span["text"].strip(), span["bbox"], span["size"], span["font"]
                        bold = "Bold" in fn
                    elif abs(span["bbox"][1] - bbox[1]) < 3:
                        text += " " + span["text"].strip()
                        if span["size"] > fs: fs, fn, bold = span["size"], span["font"], "Bold" in span["font"]
                if text and is_valid(text):
                    all_items.append({"text": text, "bbox": bbox, "fs": fs, "bold": bold})
    
    if not all_items: return pd.DataFrame()
    mean_fs = np.mean([item["fs"] for item in all_items])
    
    # Extract features
    for page_num, page in enumerate(doc):
        ph = page.rect.height
        for block in page.get_text("dict")["blocks"]:
            if block['type'] != 0: continue
            for line in block["lines"]:
                if not line["spans"]: continue
                text, bbox, fs, bold = "", None, 0, False
                for span in line["spans"]:
                    if is_watermark(span, ph, page.rect.width) or not span["text"].strip(): continue
                    if bbox is None:
                        text, bbox, fs = span["text"].strip(), span["bbox"], span["size"]
                        bold = "Bold" in span["font"]
                    elif abs(span["bbox"][1] - bbox[1]) < 3:
                        text += " " + span["text"].strip()
                        if span["size"] > fs: fs, bold = span["size"], "Bold" in span["font"]
                
                if text and is_valid(text) and not is_toc(text, fs, mean_fs):
                    data.append({
                        "page": page_num + 1, "text": text, "font_size": fs, "bold": int(bold),
                        "x0": bbox[0], "y0": bbox[1], 
                        "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text),
                        "length": len(text)
                    })
    
    doc.close()
    return pd.DataFrame(data)

def create_structured_output(df):
    """Create hierarchical JSON structure with title and outline"""
    # Find title
    title_rows = df[df["predicted"] == "TITLE"]
    title = title_rows.iloc[0]["text"] if not title_rows.empty else "Untitled Document"
    
    # Create outline from headings and content
    outline = []
    for _, row in df.iterrows():
        if row["predicted"] != "TITLE":  # Exclude title from outline
            outline.append({
                "page": int(row["page"]),
                "text": row["text"],
                "label": row["predicted"]
            })
    
    return {
        "title": title,
        "outline": outline
    }

# Docker-friendly PDF processing
def process_input_folder():
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    if not os.path.exists(input_dir):
        print("❌ Input directory not found. Mount your input folder to /app/input")
        return
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in input directory")
        return
    
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        print(f"Processing: {pdf_file}")
        
        try:
            df_new = predict_pdf(pdf_path)
            if not df_new.empty:
                features = ["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]
                df_new["predicted"] = model.predict(df_new[features])
                
                # Ensure single TITLE
                titles = df_new[df_new["predicted"] == "TITLE"]
                if len(titles) > 1:
                    max_idx = titles["font_size"].idxmax()
                    df_new.loc[titles.index, "predicted"] = "H1"
                    df_new.loc[max_idx, "predicted"] = "TITLE"
                
                # Create structured output
                structured_output = create_structured_output(df_new)
                
                # Save output
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}_labels.json")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(structured_output, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {pdf_file}: {len(df_new)} items. Labels: {dict(df_new['predicted'].value_counts())}")
                print(f"✅ Output: {output_file}")
            else:
                print(f"❌ {pdf_file}: No valid text extracted")
        
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {e}")

# Interactive mode vs Docker mode
if os.path.exists("/app/input"):
    # Docker mode - process all PDFs in input folder
    process_input_folder()
else:
    # Interactive mode
    try:
        pdf_path = input("Enter PDF location: ")
        if os.path.exists(pdf_path) and model is not None:
            df_new = predict_pdf(pdf_path)
            if not df_new.empty:
                features = ["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]
                df_new["predicted"] = model.predict(df_new[features])
                
                # Ensure single TITLE
                titles = df_new[df_new["predicted"] == "TITLE"]
                if len(titles) > 1:
                    max_idx = titles["font_size"].idxmax()
                    df_new.loc[titles.index, "predicted"] = "H1"
                    df_new.loc[max_idx, "predicted"] = "TITLE"
                
                # Create structured output
                structured_output = create_structured_output(df_new)
                
                os.makedirs("output", exist_ok=True)
                with open("output/predicted_labels_output.json", 'w', encoding='utf-8') as f:
                    json.dump(structured_output, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Processed {len(df_new)} items. Labels: {dict(df_new['predicted'].value_counts())}")
                print(f"✅ Saved to: {os.path.abspath('output/predicted_labels_output.json')}")
            else:
                print("❌ No valid text extracted")
        else:
            print("❌ File not found or model not trained")
    except Exception as e:
        print(f"❌ Error: {e}")