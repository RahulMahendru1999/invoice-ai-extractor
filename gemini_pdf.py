# -----------------------------
# 1. Restart Python Environment
# -----------------------------
dbutils.library.restartPython()

# -----------------------------
# 2. Install Required Packages
# -----------------------------
%pip install pypdf
%pip install --upgrade pip
%pip install --upgrade google-genai pydantic typing_extensions

# -----------------------------
# 3. Imports
# -----------------------------
from pypdf import PdfReader
from google import genai
import json
import os
import time

# -----------------------------
# 4. Gemini Client Setup
# -----------------------------
# ⚠️ Recommended: store API key in Databricks Secret instead of hardcoding
# Example: dbutils.secrets.get(scope="my_scope", key="gemini_api_key")

client = genai.Client(
    api_key="YOUR_API_KEY_HERE"
)

# -----------------------------
# 5. PDF File Paths
# -----------------------------
pdf_files = [
    "/Workspace/Users/rahulmahendru1999@gmail.com/pload/Memo_1F.pdf",
    "/Workspace/Users/rahulmahendru1999@gmail.com/pload/Memo_In.pdf",
    "/Workspace/Users/rahulmahendru1999@gmail.com/pload/Memo_Sam.PDF"
]

# -----------------------------
# 6. Processing Logic
# -----------------------------
results = []

for pdf_path in pdf_files:

    print(f"\nProcessing File: {os.path.basename(pdf_path)}")

    try:
        # -------------------------
        # Extract Text from PDF
        # -------------------------
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        # Limit text size for token control
        text = text[:5000]

        # -------------------------
        # Prompt for Gemini
        # -------------------------
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

        # -------------------------
        # Call Gemini Model
        # -------------------------
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        output = response.text.strip()

        print("\nAI Output:")
        print(output)

        # -------------------------
        # Store Result
        # -------------------------
        results.append({
            "file_name": os.path.basename(pdf_path),
            "response": output
        })

        # -------------------------
        # Rate limit handling
        # -------------------------
        print("\nWaiting 45 seconds to avoid API quota limits...")
        time.sleep(45)

    except Exception as e:
        print("\nError Processing File:")
        print(str(e))

# -----------------------------
# 7. Final Output
# -----------------------------
print("\nProcessing Completed")

print(json.dumps(results, indent=4))