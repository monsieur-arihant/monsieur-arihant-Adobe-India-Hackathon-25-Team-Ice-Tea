import fitz, requests, os, re, pandas as pd, numpy as np, json
from sklearn.ensemble import RandomForestClassifier
from collections import Counter

os.makedirs("pdf_dataset", exist_ok=True)

# Download training PDFs
urls = ["https://arxiv.org/pdf/1706.03762.pdf", "https://arxiv.org/pdf/1605.08294.pdf", 
        "https://arxiv.org/pdf/1802.05365.pdf", "https://arxiv.org/pdf/1409.0473.pdf",
        "https://arxiv.org/pdf/1512.03385.pdf", "https://arxiv.org/pdf/1506.01497.pdf"]

for i, url in enumerate(urls, 1):
    try:
        r = requests.get(url, timeout=30)
        if len(r.content) <= 48*1024*1024:
            with open(f"pdf_dataset/sample_{i}.pdf", "wb") as f: 
                f.write(r.content)
            print(f"Downloaded sample_{i}.pdf")
    except: pass

def is_valid(text):
    text = text.strip()
    return (text and len(text) > 1 and not re.match(r"[^\w\s]+$|.*\.{3,}\s*\d+$|^[\d\s.()ivxlcdm]{1,8}$|^[.\-_]{3,}$", text) 
            and not re.search(r"https?://|www\.|@") and (len(set(text.replace(' ', ''))) > 2 or len(text) >= 10))

def is_margin(span, ph, pw):
    y, x, fs = span["bbox"][1], span["bbox"][0], span["size"]
    return (span.get("alpha", 1) < 0.5 or fs > 50 or fs < 6 or 
            y < 0.03*ph or y > 0.97*ph or x < 0.03*pw or x > 0.97*pw)

def is_toc(text, fs, mean_fs):
    return (re.search(r"\.{2,}\s*\d+\s*$", text) or 
            re.match(r"^\d+(\.\d+)*\s+[A-Za-z]", text) and fs < mean_fs*0.95 or
            re.match(r"^(table of contents|contents|index)$", text.lower()))

def get_features(text, bbox, fs, font, ph, pw, mean_fs, page, total_pages):
    t = text.strip()
    return {
        'font_size': fs, 'font_ratio': fs/mean_fs, 'is_bold': int("bold" in font.lower()),
        'x_ratio': bbox[0]/pw, 'y_ratio': bbox[1]/ph, 'page_ratio': page/total_pages,
        'length': len(t), 'upper_ratio': sum(c.isupper() for c in t)/max(len(t), 1),
        'starts_section': int(bool(re.match(r"^\d+(\.\d+)*\s", t))),
        'ends_colon': int(t.endswith(':')), 'is_all_caps': int(t.isupper() and len(t) > 1),
        'has_title_words': int(bool(re.search(r"\b(chapter|section|part|appendix|introduction|conclusion|abstract|summary|background|results|references)\b", t.lower())))
    }

def classify(text, features, page):
    t, fr, bold, yr, length = text.strip(), features['font_ratio'], features['is_bold'], features['y_ratio'], features['length']
    
    if page <= 3 and fr >= 1.4 and (bold or features['is_all_caps']) and yr < 0.4 and length > 10:
        return "TITLE"
    elif re.match(r"^\d+\s+[A-Z]", t) or (fr >= 1.25 and bold and features['has_title_words']) or (fr >= 1.3 and bold and length < 100):
        return "H1"  
    elif re.match(r"^\d+\.\d+\s+[A-Z]", t) or (fr >= 1.15 and bold) or (bold and features['ends_colon'] and length < 80):
        return "H2"
    elif re.match(r"^\d+\.\d+\.\d+\s+[A-Z]", t) or (fr >= 1.05 and (bold or features['upper_ratio'] > 0.7)) or (bold and length < 60):
        return "H3"
    elif re.match(r"^\d+\.\d+\.\d+\.\d+\s+[A-Z]", t) or (fr >= 1.02 and bold and length < 50) or (features['upper_ratio'] > 0.5 and length < 40):
        return "H4"
    return "P"

def extract_text(doc):
    items, data = [], []
    total_pages = len(doc)
    
    # Collect all text for stats
    for page_num, page in enumerate(doc):
        ph, pw = page.rect.height, page.rect.width
        for block in page.get_text("dict")["blocks"]:
            if block.get('type') != 0: continue
            for line in block["lines"]:
                if not line.get("spans"): continue
                
                text, bbox, fs, font = "", None, 0, ""
                for span in line["spans"]:
                    if is_margin(span, ph, pw) or not span["text"].strip(): continue
                    if bbox is None:
                        text, bbox, fs, font = span["text"].strip(), list(span["bbox"]), span["size"], span["font"]
                    elif abs(span["bbox"][1] - bbox[1]) < 3:
                        text += " " + span["text"].strip()
                        bbox[2] = max(bbox[2], span["bbox"][2])
                        if span["size"] > fs: fs, font = span["size"], span["font"]
                
                if text and is_valid(text):
                    items.append({"text": text, "bbox": bbox, "fs": fs, "font": font, "page": page_num + 1})
    
    if not items: return []
    mean_fs = np.mean([item["fs"] for item in items])
    
    # Extract features and classify
    for item in items:
        if is_toc(item["text"], item["fs"], mean_fs): continue
        
        page = doc[item["page"] - 1]
        features = get_features(item["text"], item["bbox"], item["fs"], item["font"], 
                               page.rect.height, page.rect.width, mean_fs, item["page"], total_pages)
        
        label = classify(item["text"], features, item["page"])
        data.append({"text": item["text"], "page": item["page"], "label": label, **features})
    
    return data

# Process training data
all_data = []
for f in os.listdir("pdf_dataset"):
    if f.endswith(".pdf"):
        print(f"Processing: {f}")
        doc = fitz.open(f"pdf_dataset/{f}")
        pdf_data = extract_text(doc)
        for item in pdf_data: item["filename"] = f
        all_data.extend(pdf_data)
        doc.close()

model = None
if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv("pdf_dataset/labels.csv", index=False)
    print(f"Dataset: {len(df)} items, Labels: {dict(df['label'].value_counts())}")
    
    # Train model
    features = ['font_size', 'font_ratio', 'is_bold', 'x_ratio', 'y_ratio', 'page_ratio', 
               'length', 'upper_ratio', 'starts_section', 'ends_colon', 'is_all_caps', 'has_title_words']
    model = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
    model.fit(df[features], df['label'])
    print("Model trained.")

def predict_pdf(pdf_path):
    if not model: return pd.DataFrame()
    
    doc = fitz.open(pdf_path)
    data = extract_text(doc)
    doc.close()
    
    if not data: return pd.DataFrame()
    
    df = pd.DataFrame(data)
    features = ['font_size', 'font_ratio', 'is_bold', 'x_ratio', 'y_ratio', 'page_ratio',
               'length', 'upper_ratio', 'starts_section', 'ends_colon', 'is_all_caps', 'has_title_words']
    df["predicted"] = model.predict(df[features])
    
    # Ensure single title
    titles = df[df["predicted"] == "TITLE"]
    if len(titles) > 1:
        best_idx = titles.sort_values(['page', 'font_size'], ascending=[True, False]).index[0]
        df.loc[titles.index, "predicted"] = "H1"
        df.loc[best_idx, "predicted"] = "TITLE"
    
    return df

def create_output(df):
    title_row = df[df["predicted"] == "TITLE"]
    title = title_row.iloc[0]["text"] if not title_row.empty else "Untitled Document"
    
    outline = [{"level": row["predicted"], "text": row["text"], "page": int(row["page"])} 
               for _, row in df.iterrows() if row["predicted"] != "TITLE"]
    
    return {"title": title, "outline": outline}

def process_folder():
    input_dir, output_dir = "/app/input", "/app/output"
    if not os.path.exists(input_dir):
        print("❌ Mount input folder to /app/input")
        return
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDFs found")
        return
    
    for pdf_file in pdf_files:
        try:
            df = predict_pdf(os.path.join(input_dir, pdf_file))
            if not df.empty:
                output = create_output(df)
                os.makedirs(output_dir, exist_ok=True)
                with open(f"{output_dir}/{os.path.splitext(pdf_file)[0]}_labels.json", 'w') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                print(f"✅ {pdf_file}: {len(df)} items, {dict(df['predicted'].value_counts())}")
            else:
                print(f"❌ {pdf_file}: No text extracted")
        except Exception as e:
            print(f"❌ {pdf_file}: {e}")

# Main execution
if os.path.exists("/app/input"):
    process_folder()
else:
    try:
        pdf_path = input("Enter PDF path: ")
        if os.path.exists(pdf_path) and model:
            df = predict_pdf(pdf_path)
            if not df.empty:
                output = create_output(df)
                os.makedirs("output", exist_ok=True)
                with open("output/predicted_labels.json", 'w') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                print(f"✅ {len(df)} items, Labels: {dict(df['predicted'].value_counts())}")
            else:
                print("❌ No text extracted")
        else:
            print("❌ File not found or model not trained")
    except Exception as e:
        print(f"❌ Error: {e}")