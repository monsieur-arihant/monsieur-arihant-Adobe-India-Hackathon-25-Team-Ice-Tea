


import fitz  # PyMuPDF

import string

import requests
import os
import re

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

os.makedirs("pdf_dataset", exist_ok=True)

# List of sample open-access academic paper URLs
pdf_urls = [
    "https://arxiv.org/pdf/1706.03762.pdf"
    "https://arxiv.org/pdf/1605.08294.pdf",  # Neural Machine Translation
    "https://arxiv.org/pdf/1802.05365.pdf",  # BERT
    "https://arxiv.org/pdf/1409.0473.pdf",   # Deep Learning Review
    "https://arxiv.org/pdf/1512.03385.pdf",  # ResNet
    "https://arxiv.org/pdf/1506.01497.pdf",  # Batch Normalization
    "https://arxiv.org/pdf/1312.6114.pdf",   # VGGNet
    "https://arxiv.org/pdf/1807.03819.pdf",  # ULMFiT
    "https://arxiv.org/pdf/1906.08237.pdf",  # XLNet
    "https://arxiv.org/pdf/1706.03762v5.pdf" # Newer version of Attention
]

# Download loop
for i, url in enumerate(pdf_urls, 1):
    try:
        response = requests.get(url, timeout=10)
        filename = f"pdf_dataset/sample_{i}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")


def is_meaningful(text):
    """
    Filters out junk symbols, page numbers, index dots, etc.
    """
    if not text or len(text.strip()) <= 1:
        return False

    text = text.strip()

    if re.fullmatch(r"[^\w\s]+", text):
        return False

    junk_symbols = {"†", "•", "*", "¶", "§", "~", "-", "–", "—", "→", "⇒", "©", "®", "™", ".", "|"}
    if all(char in junk_symbols for char in text):
        return False

    if text.isdigit() and len(text) <= 3:
        return False

    if re.match(r".*\.{3,}\s*\d+$", text):  
        return False

    return True

def looks_like_watermark(span, page_height):
    y_pos = span["bbox"][1]
    font_size = span["size"]
    opacity = span.get("alpha", 1)

    return (
        opacity < 0.5 or
        (font_size > 30 and y_pos < 0.2 * page_height) or
        ("watermark" in span.get("font", "").lower())
    )

data = []

for filename in os.listdir("pdf_dataset"):
    if filename.endswith(".pdf"):
        doc = fitz.open(f"pdf_dataset/{filename}")
        for page_num, page in enumerate(doc):
            page_height = page.rect.height
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0:
                    for line in block["lines"]:
                        spans = line["spans"]
                        if not spans:
                            continue
                        merged_text = spans[0]["text"].strip()
                        ref_span = spans[0]

                        for span in spans[1:]:
                            if looks_like_watermark(span, page_height):
                                continue
                            if (
                                abs(span["bbox"][1] - ref_span["bbox"][1]) < 2 and
                                (span["bbox"][0] - ref_span["bbox"][2]) < 20
                            ):
                                merged_text += " " + span["text"].strip()
                                ref_span["bbox"] = (
                                    ref_span["bbox"][0],
                                    ref_span["bbox"][1],
                                    span["bbox"][2],
                                    span["bbox"][3]
                                )
                            else:
                                if is_meaningful(merged_text):
                                    data.append({
                                        "filename": filename,
                                        "page": page_num + 1,
                                        "text": merged_text,
                                        "font_size": ref_span["size"],
                                        "font_name": ref_span["font"],
                                        "bold": "Bold" in ref_span["font"],
                                        "x0": ref_span["bbox"][0],
                                        "y0": ref_span["bbox"][1],
                                        "uppercase_ratio": sum(1 for c in merged_text if c.isupper()) / len(merged_text),
                                        "length": len(merged_text),
                                    })
                                ref_span = span
                                merged_text = span["text"].strip()

                        if is_meaningful(merged_text) and not looks_like_watermark(ref_span, page_height):
                            data.append({
                                "filename": filename,
                                "page": page_num + 1,
                                "text": merged_text,
                                "font_size": ref_span["size"],
                                "font_name": ref_span["font"],
                                "bold": "Bold" in ref_span["font"],
                                "x0": ref_span["bbox"][0],
                                "y0": ref_span["bbox"][1],
                                "uppercase_ratio": sum(1 for c in merged_text if c.isupper()) / len(merged_text),
                                "length": len(merged_text),
                            })
        doc.close()

df = pd.DataFrame(data)


mean_font = df["font_size"].mean()

def label_row(row):
    text = row["text"].strip()
    font = row["font_size"]
    bold = row["bold"]
    upper = row["uppercase_ratio"]

    # Pattern-based
    if re.match(r"^\d+\.\d+\.\d+(\s|$)", text):
        return "H3"
    elif re.match(r"^\d+\.\d+(\s|$)", text):
        return "H2"
    elif re.match(r"^\d+(\s|$)", text):
        return "H1"

    # Adaptive font-size logic based on mean
    if font >= mean_font + 6:
        return "TITLE"
    elif font >= mean_font + 3 and bold:
        return "H1"
    elif font >= mean_font + 1.5 and bold:
        return "H2"
    elif font >= mean_font - 0.5:
        return "H3"
    else:
        return "P"

df["label"] = df.apply(label_row, axis=1)


df.to_csv("pdf_dataset/heading_labels_enhanced.csv", index=False, escapechar='\\')
print("Cleaned & labeled output saved to: pdf_dataset/heading_labels_enhanced.csv.csv")





from sklearn.ensemble import RandomForestClassifier
import pandas as pd

# Load the preprocessed dataset
df = pd.read_csv("pdf_dataset/heading_labels_enhanced.csv")

# Convert 'bold' boolean to integer (if not already)
df["bold"] = df["bold"].astype(int)

# Define features and target label
features = df[["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]]
labels = df["label"]

# Train the RandomForest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(features, labels)

print("Model trained successfully.")


def extract_features_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    data = []
    for page_num, page in enumerate(doc):
        page_height = page.rect.height
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                for line in block["lines"]:
                    spans = line["spans"]
                    if not spans:
                        continue
                    merged_text = spans[0]["text"].strip()
                    ref_span = spans[0]

                    for span in spans[1:]:
                        if looks_like_watermark(span, page_height):
                            continue
                        if (
                            abs(span["bbox"][1] - ref_span["bbox"][1]) < 2 and
                            (span["bbox"][0] - ref_span["bbox"][2]) < 20
                        ):
                            merged_text += " " + span["text"].strip()
                            ref_span["bbox"] = (
                                ref_span["bbox"][0],
                                ref_span["bbox"][1],
                                span["bbox"][2],
                                span["bbox"][3]
                            )
                        else:
                            if is_meaningful(merged_text):
                                data.append({
                                    "filename": os.path.basename(pdf_path),
                                    "page": page_num + 1,
                                    "text": merged_text,
                                    "font_size": ref_span["size"],
                                    "font_name": ref_span["font"],
                                    "bold": int("Bold" in ref_span["font"]),
                                    "x0": ref_span["bbox"][0],
                                    "y0": ref_span["bbox"][1],
                                    "uppercase_ratio": sum(1 for c in merged_text if c.isupper()) / len(merged_text),
                                    "length": len(merged_text),
                                })
                            ref_span = span
                            merged_text = span["text"].strip()

                    if is_meaningful(merged_text) and not looks_like_watermark(ref_span, page_height):
                        data.append({
                            "filename": os.path.basename(pdf_path),
                            "page": page_num + 1,
                            "text": merged_text,
                            "font_size": ref_span["size"],
                            "font_name": ref_span["font"],
                            "bold": int("Bold" in ref_span["font"]),
                            "x0": ref_span["bbox"][0],
                            "y0": ref_span["bbox"][1],
                            "uppercase_ratio": sum(1 for c in merged_text if c.isupper()) / len(merged_text),
                            "length": len(merged_text),
                        })
    doc.close()
    return pd.DataFrame(data)


# 👇 Input external PDF here
external_pdf_path = input("Enter the pdf file location")
df_new = extract_features_from_pdf(external_pdf_path)

# ⚠️ Check if model is already trained — otherwise raise error
required_features = ["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]
df_new["predicted"] = model.predict(df_new[required_features])

print(df_new.head())
# making sure ouput file exists
os.makedirs("output", exist_ok=True)
# 💾 Save to JSON
output_json = "output/predicted_labels_output.json"
df_new.to_json(output_json, orient="records", indent=2)
print(f"✅ Predicted labels saved to: {output_json}")