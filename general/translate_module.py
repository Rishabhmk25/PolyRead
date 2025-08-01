import re
import asyncio
#from langdetect import detect, detect_langs
from googletrans import Translator
import pyttsx3
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

translator = Translator()

# ✅ Normalize language codes for googletrans compatibility
LANG_CODE_MAP = {
    "zh": "zh-CN",
    "jp": "ja",
    "kr": "ko"
}
model = AutoModelForSequenceClassification.from_pretrained("model")
tokenizer = AutoTokenizer.from_pretrained("model")
clf = pipeline("text-classification", model=model, tokenizer=tokenizer)
def language_detection(text):
    result = clf(text)

    return result

def normalize_lang_code(lang):
    return LANG_CODE_MAP.get(lang.lower(), lang)

# ✅ Language detection with CJK script disambiguation
def detect_language(text):
    def count_cjk_scripts(text):
        counts = {
            'zh': 0,  # Chinese
            'ko': 0,  # Korean
            'ja': 0   # Japanese
        }
        for ch in text:
            code = ord(ch)
            if 0x4E00 <= code <= 0x9FFF:
                counts['zh'] += 1
            elif 0xAC00 <= code <= 0xD7AF:
                counts['ko'] += 1
            elif 0x3040 <= code <= 0x30FF or 0x31F0 <= code <= 0x31FF:
                counts['ja'] += 1
        return counts

    try:
        lang = language_detection(text)[0]['label']
        confidence = language_detection(text)[0]['score']

        if lang in ['zh-cn', 'zh', 'ko', 'ja']:
            counts = count_cjk_scripts(text)
            dominant = max(counts, key=counts.get)
            if counts[dominant] > 0:
                return dominant, confidence
        return lang, confidence

    except Exception:
        try:
            result = translator.detect(text)
            print("Fallback to googletrans.detect()")
            lang = result.lang
            counts = count_cjk_scripts(text)
            dominant = max(counts, key=counts.get)
            if counts[dominant] > 0:
                return dominant, result.confidence
            else:
                return lang, result.confidence
        except Exception:
            return None, 0

# ✅ Clean text per script
def clean_text(text, lang):
    if lang in ['hi', 'mr', 'bn', 'gu', 'pa', 'ne']:
        return re.sub(r'[^ऀ-ॿঀ-৿਀-੿\s।.,!?]', '', text)
    elif lang in ['ta', 'te']:
        return re.sub(r'[^஀-௿ఀ-౿\s।.,!?]', '', text)
    elif lang == 'kn':
        return re.sub(r'[^ಀ-೿\s।.,!?]', '', text)
    elif lang == 'ml':
        return re.sub(r'[^ഀ-ൿ\s।.,!?]', '', text)
    elif lang == 'si':
        return re.sub(r'[^඀-෿\s।.,!?]', '', text)
    elif lang == 'zh-CN' or lang == 'zh':
        return re.sub(r'[^一-鿿。，！？]', '', text)
    elif lang == 'ja':
        return text  # Japanese cleaning can be more complex; skipping
    elif lang == 'ko':
        return re.sub(r'[^가-힯\s.,!?]', '', text)
    elif lang in ['ar', 'ur']:
        return re.sub(r'[^؀-ۿ\s،؟]', '', text)
    elif lang in ['ru', 'uk', 'sr']:
        return re.sub(r'[^Ѐ-ӿ\s.,!?]', '', text)
    elif lang == 'el':
        return re.sub(r'[^Ͱ-Ͽ\s.,!?]', '', text)
    elif lang == 'he':
        return re.sub(r'[^֐-׿\s.,!?]', '', text)
    elif lang == 'th':
        return re.sub(r'[^฀-๿\s.,!?]', '', text)
    elif lang in ['de', 'es', 'nl', 'it', 'fr', 'en', 'vi', 'pl', 'cs', 'tr', 'id', 'ro']:
        return re.sub(r"[^a-zA-ZÀ-ÿĀ-žŒœẞßÇçÑñÄäÖöÜüẞẞ\s.,!?¿¡'-]", '', text)
    else:
        return re.sub(r'[^\w\s.,!?]', '', text)

# ✅ Chunk text to avoid API limit issues
def chunk_text(text, max_len=300):
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 > max_len:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_len = len(word) + 1
        else:
            current_chunk.append(word)
            current_len += len(word) + 1
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

# ✅ Translate full input text
def translate_text_input(text):
    lang_code = language_detection(text)[0]['label']
    confidence = language_detection(text)[0]['score']

    if not lang_code:
        print("Unable to detect language.")
        return None, 0, "Language detection failed."

    lang_code = normalize_lang_code(lang_code)
    cleaned = clean_text(text, lang_code)
    full_translation = ""

    def translate_chunks():
        nonlocal full_translation
        for chunk in chunk_text(cleaned):
            try:
                translated = translator.translate(chunk, src=lang_code, dest='en')
                full_translation += translated.text + " "
            except Exception as e:
                full_translation += f"[ Translation error: {e} ] "
    translate_chunks()

    return lang_code, confidence, full_translation.strip()

# ✅ Optional Text-to-Speech
def speak_text(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# ✅ Example Usage
if __name__ == "__main__":
    input_text = """请您爱护和保护我们的美丽环境。"""
    lang, confidence, translated_text = translate_text_input(input_text)
    print(f"\nDetected Language: {lang} (Confidence: {confidence})")
    print(f"Translated Text: {translated_text}")
    speak_text(translated_text)
