import fitz, requests, os, re, pandas as pd, numpy as np, json
from sklearn.ensemble import RandomForestClassifier
from collections import Counter

os.makedirs("pdf_dataset", exist_ok=True)

# Download sample PDFs
urls = ["https://arxiv.org/pdf/1706.03762.pdf", "https://arxiv.org/pdf/1605.08294.pdf", 
        "https://arxiv.org/pdf/1802.05365.pdf", "https://arxiv.org/pdf/1409.0473.pdf"]

for i, url in enumerate(urls, 1):
    try:
        r = requests.get(url, timeout=30, stream=True)
        if int(r.headers.get('content-length', 0)) > 50*1024*1024: continue
        with open(f"pdf_dataset/sample_{i}.pdf", "wb") as f: f.write(r.content)
        print(f"Downloaded sample_{i}.pdf")
    except: pass

def is_valid(text):
    text = text.strip()
    if not text or len(text) <= 2: return False
    if re.fullmatch(r"[^\w\s]+", text): return False
    if re.match(r".*\.{3,}\s*\d+$|^[\d\s.()ivxlcdm]{1,6}$", text): return False
    return True

def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    items = []
    
    for page_num, page in enumerate(doc):
        ph, pw = page.rect.height, page.rect.width
        for block in page.get_text("dict")["blocks"]:
            if block.get('type') != 0: continue
            for line in block.get("lines", []):
                text, bbox, fs, fn, bold = "", None, 0, "", False
                for span in line.get("spans", []):
                    if not span.get("text", "").strip(): continue
                    y, x = span["bbox"][1], span["bbox"][0]
                    # Skip margins and watermarks
                    if (y < 0.05*ph or y > 0.95*ph or x < 0.05*pw or x > 0.95*pw or 
                        span.get("alpha", 1) < 0.5 or span.get("size", 12) > 60): continue
                    
                    if not text:
                        text, bbox, fs, fn = span["text"].strip(), span["bbox"], span["size"], span["font"]
                        bold = "bold" in fn.lower()
                    else:
                        text += " " + span["text"].strip()
                        fs = max(fs, span["size"])
                        if "bold" in span["font"].lower(): bold = True
                
                if text and is_valid(text):
                    items.append({
                        "text": text, "page": page_num + 1, "font_size": fs,
                        "bold": bold, "x": bbox[0], "y": bbox[1], "length": len(text)
                    })
    doc.close()
    return items

def classify_text(text, font_size, is_bold, page, body_size):
    text = text.strip()
    
    # Skip TOC entries
    if re.search(r"\.{2,}\s*\d+\s*$", text): return "P"
    
    # Numbered sections (priority)
    if re.match(r"^(\d+(?:\.\d+)*)\s+", text):
        dots = text.split()[0].count('.')
        if dots == 0: return "H1"
        elif dots == 1: return "H2"  
        elif dots == 2: return "H3"
        else: return "H4"
    
    # Title detection
    if page <= 3 and font_size >= body_size * 1.5 and (is_bold or font_size >= body_size * 1.8):
        return "TITLE"
    
    # Section keywords
    keywords = ["abstract", "introduction", "conclusion", "references", "background", 
                "methodology", "results", "discussion", "summary"]
    if any(kw in text.lower() for kw in keywords):
        return "H1" if font_size >= body_size * 1.2 or is_bold else "H2"
    
    # Font size based
    ratio = font_size / body_size
    if ratio >= 1.3 and (is_bold or len(text) < 100): return "H1"
    elif ratio >= 1.15 and (is_bold or len(text) < 80): return "H2"
    elif ratio >= 1.05 and is_bold and len(text) < 60: return "H3"
    elif is_bold and len(text) < 100: return "H3"
    
    return "P"

def process_pdf(pdf_path):
    items = extract_text_blocks(pdf_path)
    if not items: return pd.DataFrame()
    
    # Find body text size (most common)
    sizes = [item["font_size"] for item in items]
    body_size = Counter([round(s, 1) for s in sizes]).most_common(1)[0][0]
    
    data = []
    for item in items:
        label = classify_text(item["text"], item["font_size"], item["bold"], 
                            item["page"], body_size)
        
        data.append({
            "page": item["page"], "text": item["text"], "font_size": item["font_size"],
            "bold": int(item["bold"]), "x0": item["x"], "y0": item["y"],
            "length": item["length"], 
            "uppercase_ratio": sum(c.isupper() for c in item["text"]) / len(item["text"]),
            "predicted": label
        })
    
    return pd.DataFrame(data)

def create_output(df):
    if df.empty: return {"title": "Untitled Document", "outline": []}
    
    # Find title
    titles = df[df["predicted"] == "TITLE"]
    title = titles.iloc[0]["text"] if not titles.empty else "Untitled Document"
    
    # Create outline
    outline = []
    for _, row in df.iterrows():
        if row["predicted"] != "TITLE":
            outline.append({
                "level": row["predicted"],
                "text": row["text"], 
                "page": int(row["page"])
            })
    
    return {"title": title, "outline": outline}

# Train basic model
print("Processing training data...")
all_data = []
for f in os.listdir("pdf_dataset"):
    if f.endswith(".pdf"):
        try:
            df = process_pdf(f"pdf_dataset/{f}")
            if not df.empty: all_data.append(df)
        except Exception as e: print(f"Error with {f}: {e}")

if all_data:
    train_df = pd.concat(all_data, ignore_index=True)
    features = ["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]
    if len(train_df['predicted'].unique()) > 2:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(train_df[features], train_df["predicted"])
        print("Model trained.")
    else: model = None
else: model = None

# Docker vs Interactive mode
if os.path.exists("/app/input"):
    print("🐳 Docker mode")
    for pdf_file in os.listdir("/app/input"):
        if pdf_file.lower().endswith('.pdf'):
            try:
                df = process_pdf(f"/app/input/{pdf_file}")
                if not df.empty:
                    # Ensure single title
                    titles = df[df["predicted"] == "TITLE"]
                    if len(titles) > 1:
                        max_idx = titles["font_size"].idxmax()
                        df.loc[titles.index, "predicted"] = "H1"
                        df.loc[max_idx, "predicted"] = "TITLE"
                    
                    output = create_output(df)
                    os.makedirs("/app/output", exist_ok=True)
                    with open(f"/app/output/{pdf_file[:-4]}_labels.json", 'w') as f:
                        json.dump(output, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ {pdf_file}: {len(df)} items, {dict(df['predicted'].value_counts())}")
            except Exception as e:
                print(f"❌ {pdf_file}: {e}")
else:
    print("💻 Interactive mode")
    pdf_path = input("Enter PDF path: ")
    if os.path.exists(pdf_path):
        df = process_pdf(pdf_path)
        if not df.empty:
            titles = df[df["predicted"] == "TITLE"]
            if len(titles) > 1:
                max_idx = titles["font_size"].idxmax()
                df.loc[titles.index, "predicted"] = "H1"
                df.loc[max_idx, "predicted"] = "TITLE"
            
            output = create_output(df)
            os.makedirs("output", exist_ok=True)
            with open("output/result.json", 'w') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved: {dict(df['predicted'].value_counts())}")