from paddleocr import PPStructureV3
from rich.console import Console
import os
import time

s = time.time()

console = Console()
pipeline = PPStructureV3(use_seal_recognition=False, use_formula_recognition=False)

image_path = "1.png"
output = pipeline.predict(image_path)

save_folder = "output"
base_filename = os.path.splitext(os.path.basename(image_path))[0]
md_path = os.path.join(save_folder, base_filename + ".md")

# Clear old markdown file to avoid duplication
if os.path.exists(md_path):
    os.remove(md_path)

for res in output:
    res.print()
    res.save_to_json(save_path=save_folder)
    res.save_to_markdown(save_path=save_folder)

# ✅ Load and print cleaned markdown
if os.path.exists(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    seen = set()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            cleaned_lines.append(line)

    cleaned_md_content = "".join(cleaned_lines)

    console.rule(f"[bold blue]📄 Cleaned Markdown Output: {base_filename}")
    console.print(cleaned_md_content, markup=False)
e = time.time()
print(f"Time taken = {e-s}sec")