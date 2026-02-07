import os
import pymupdf4llm
import re

# 1. Setup Paths
source_folder = r"C:\Users\Shaziya khan\Desktop\Somyali_backend_project\Data"
output_folder = r"C:\Users\Shaziya khan\Desktop\Somyali_backend_project\Data\md_files"
os.makedirs(output_folder, exist_ok=True)

print(f" Scanning '{source_folder}' for PDFs...")  

# 2. Loop through every file
converted_count = 0
for filename in os.listdir(source_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(source_folder, filename)
        md_filename = filename.replace(".pdf", ".md")
        md_path = os.path.join(output_folder, md_filename)

        print(f"\n Processing: {filename}...")

        try:
            # 3. Convert to Markdown
            md_text = pymupdf4llm.to_markdown(pdf_path)

            # 4. Remove page numbers
            md_text = re.sub(r'\nPage \d+\n', '\n', md_text)

            # 5. Save as Markdown
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_text)

            print(f"   ✅ Saved to: {md_filename}")
            converted_count += 1
 
        except Exception as e:
            print(f" Error converting {filename}: {e}")

print(f"\n🎉 Finished! Converted {converted_count} documents to Markdown.")
print("You can now find them in the 'md_files' folder.")
