from ocr_module import run_ocr
from translate_module import translate_text_input, speak_text  # 👈 All needed functions
import time
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from collections import Counter
from load import language_detection


if __name__ == "__main__":
    image_path = "c.png" # 🔸 Use raw string to avoid path errors

    print("🔍 Running OCR Pipeline...")
    extracted_texts = run_ocr(image_path)
    print(extracted_texts)
    if not extracted_texts:
        print("❌ No text detected.")
    else:
        # ✅ Print organized OCR results with per-line language detection
        print("\n✅ Extracted Texts with Coordinates and Language Detection:")
        all_text = []

        for idx, item in enumerate(extracted_texts[0], 1):
            text = item["text"]
            conf = item["confidence"]
            coords = item["coordinates"]
            print(f"{idx}: {text} (Confidence: {conf:.3f})")
            print(f"    Coordinates: {coords}") 
            all_text.append(text)

        # ✅ Combine all detected texts into one string
        full_text = ' '.join(all_text)
        print(full_text)
        
        result5 = language_detection(full_text)
        
        # # Extract only the language labels
        # labels = [pred['label'] for pred in result5]

        # # Count the frequency of each label
        # label_counts = Counter(labels)

        # # Get the most common language
        # most_common_lang, count = label_counts.most_common(1)[0]

        print(f"Most likely language: {result5} ")

        # 🌐 Translation (no print for detected language or input text)
        _, _, translated_text = translate_text_input(full_text)

        if translated_text.strip() == "":
            print("❌ Translation failed or empty.")
        else:
            print(f"\n✅ Final Output:")
            print(f"Translated Text: {translated_text}")

            # 🔊 Text-to-Speech\
            print("\n 🎙️ To listen translated text type y")
            t = input()
            if(t.lower() == 'y'):
                print("\n🗣 Speaking the translated text...")
                e = time.time()
                speak_text(translated_text)