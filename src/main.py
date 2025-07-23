
# !pip install pandas scikit-learn
# !pip install PyMuPDF

import fitz  # PyMuPDF

import string

import requests
import os

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
        print(f"✅ Downloaded: {filename}")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")


data = []

def is_meaningful(text):
    # Only keep lines with alphanumeric content, punctuation, etc.
    text = text.strip()
    if not text:
        return False
    # Remove junk symbols (like '†', '•', etc.)
    allowed_chars = string.ascii_letters + string.digits + string.punctuation + ' '
    cleaned = ''.join(c for c in text if c in allowed_chars)
    return len(cleaned.strip()) >= 3  # Keep only if at least 3 good characters

for filename in os.listdir("pdf_dataset"):
    if filename.endswith(".pdf"):
        doc = fitz.open(f"pdf_dataset/{filename}")
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if not is_meaningful(text):
                                continue
                            data.append({
                                "filename": filename,
                                "page": page_num + 1,
                                "text": text,
                                "font_size": span["size"],
                                "font_name": span["font"],
                                "bold": "Bold" in span["font"],
                                "x0": span["bbox"][0],
                                "y0": span["bbox"][1],
                                "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text),
                                "length": len(text),
                            })
        doc.close()  # Safe cleanup

# Create DataFrame
df = pd.DataFrame(data)



# Label function for heading classification
# Rule-based labeling
mean_font = df["font_size"].mean()
std_font = df["font_size"].std()

def label_row(row, mean, std):
    font = row["font_size"]
    bold = row["bold"]
    upper = row["uppercase_ratio"]

    if font >= mean + 2 * std:
        return "TITLE"
    elif font >= mean + 1.5 * std:
        if bold and upper > 0.5:
            return "H1"
        else:
            return "H2"
    elif font >= mean + 0.75 * std:
        if bold:
            return "H2"
        else:
            return "H3"
    elif font >= mean:
        return "H3"
    else:
        return "P"

df["label"] = df.apply(lambda row: label_row(row, mean_font, std_font), axis=1)


# Save labeled output
output_path = "pdf_dataset/heading_labels_enhanced.csv"
df.to_csv(output_path, index=False)
print(f"✅ Enhanced labeled data saved to: {output_path}")




# Step 1: Load preprocessed dataset with features
df = pd.read_csv("pdf_dataset/heading_labels_enhanced.csv")

# Step 2: Convert boolean 'bold' column to integer
df["bold"] = df["bold"].astype(int)

# Step 3: Select features and target label
features = df[["font_size", "x0", "y0", "bold", "uppercase_ratio", "length"]]
labels = df["label"]

# Step 4: Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42
)

# Step 5: Train the RandomForest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 6: Predict on the test set and evaluate
y_pred = model.predict(X_test)
print("📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Step 7: Predict on the entire dataset
df["predicted"] = model.predict(features)

# Step 8: Save results to CSV and JSON
csv_output_path = "pdf_dataset/labeled_output.csv"
json_output_path = "pdf_dataset/labeled_output.json"

df.to_csv(csv_output_path, index=False)
df.to_json(json_output_path, orient="records", indent=2)

# Step 9: Preview sample results
print("\n📄 Sample Predictions:")
print(df[["text", "predicted"]].head(20))

# Step 10: Confirm file paths

print(f"\n✅ CSV saved to: {os.path.abspath(csv_output_path)}")
print(f"✅ JSON saved to: {os.path.abspath(json_output_path)}")
