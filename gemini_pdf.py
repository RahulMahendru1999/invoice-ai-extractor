

# -----------------------------
# 1. Install Required Packages
# -----------------------------
%pip install --force-reinstall typing_extensions>=4.12.0 google-genai pydantic pypdf openpyxl

# -----------------------------
# 2. Restart Python Environment
# -----------------------------
dbutils.library.restartPython()

# -----------------------------
# 3. Imports
# -----------------------------
from pypdf import PdfReader
from google import genai
import json
import os
import time
import re
import pandas as pd
 
# Gemini Client
client = genai.Client(api_key="YOUR_API_KEY")
 
# PDF Files
pdf_files = [
    "/Workspace/Users/rahulmahendru1999@gmail.com/pload/Memo_1Fii_.pdf",
    "/Workspace/Users/rahulmahendru1999@gmail.com/pload/Memo_Inv.pdf",
    "/Workspace/Users/rahulmahendru1999@gmail.com/pload/Memo_Sa.PDF"
]
 
results = []
 
# Loop Through PDFs
for pdf_path in pdf_files:
    print(f"\nProcessing File: {os.path.basename(pdf_path)}")
 
    try:
        # Read PDF
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
 
        # Reduce token usage
        text = text[:5000]
 
        # Prompt
        prompt = f"""
        Extract the following fields from this invoice:
 
        - vendor_name
        - invoice_number
        - invoice_date
        - total_amount
 
        Return ONLY valid JSON.
 
        Invoice Text:
        {text}
        """
 
        # Send to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
 
        # Get Output
        output = response.text.strip()
        print("\nAI Output:")
        print(output)
 
        # Save Result
        results.append({
            "file_name": os.path.basename(pdf_path),
            "response": output
        })
 
        # Wait to avoid quota limits
        print("\nWaiting 10 seconds...")
        time.sleep(10)
 
    except Exception as e:
        print(f"\nError Processing File:")
        print(str(e))
 
# Parse and clean results
clean_results = []
for r in results:
    raw = r["response"]
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"vendor_name": "", "invoice_number": "", "invoice_date": "", "total_amount": ""}
    clean_results.append({
        "file_name": r["file_name"],
        **parsed
    })
 
# Create DataFrame
df_results = pd.DataFrame(clean_results)
 
# Fix mixed types in total_amount
df_results["total_amount"] = (
    df_results["total_amount"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("$", "", regex=False)
    .astype(float)
)
 
print("\nProcessing Completed")
display(df_results)
 
# Save to Excel
output_path = "/Workspace/Users/rahulmahendru1999@gmail.com/pload/Invoice_Extracted_Results.xlsx"
df_results.to_excel(output_path, index=False)
print(f"\nFile saved: {output_path}")
