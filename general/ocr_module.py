import os
import cv2
import numpy as np
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# ------------------------------------------
# 📷 Preprocess Image for Better Detection
# ------------------------------------------
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot load image from path: {image_path}")

    # Resize to width 800 if smaller
    if image.shape[1] < 800:
        scale = 800 / image.shape[1]
        image = cv2.resize(image, (800, int(image.shape[0] * scale)))

    processed_path = 'processed_image.jpg'
    cv2.imwrite(processed_path, image)

    return processed_path

# --------------------------------------------------
# 🧠 Smart Filter to Remove Tiny or Low-Conf Boxes
# --------------------------------------------------
def filter_small_boxes(result, min_width=15, min_height=10, min_area=100, min_conf=0.36):
    filtered = []
    for line in result[0]:
        box = line[0]
        conf = line[1][1]

        x_coords = [pt[0] for pt in box]
        y_coords = [pt[1] for pt in box]
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        area = width * height

        # Filter based on size and confidence
        if width >= min_width and height >= min_height and area >= min_area and conf >= min_conf:
            filtered.append(line)

    return [filtered]

# ---------------------------------------------------
# 🖼️ Draw and Save OCR Boxes with Recognized Labels
# ---------------------------------------------------
def visualize_with_labels(image_path, result):
    image = Image.open(image_path).convert('RGB')

    boxes = [line[0] for line in result[0]]
    texts = [line[1][0] for line in result[0]]
    scores = [line[1][1] for line in result[0]]

    image_with_boxes = draw_ocr(
        image,
        boxes,
        texts,
        scores,
        font_path='C:/Windows/Fonts/msgothic.ttc'
    )

    output_path = 'detected_output_with_labels.jpg'
    image_with_boxes = cv2.cvtColor(np.array(image_with_boxes), cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, image_with_boxes)

    print(f"🖼️ Labeled bounding box image saved at: {output_path}")
    # cv2.imshow('Detected Text with Labels', image_with_boxes)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

# ---------------------------------------------------
# 🚀 Main OCR Pipeline (Detection + Filtering)
# ---------------------------------------------------
def run_ocr(image_path, lang=None):
    image = cv2.imread(image_path)
    min_side = min(image.shape[:2])
    det_limit_side_len = 960 if min_side < 1000 else 1216
    processed_image = preprocess_image(image_path)
    print(f"🛠️ Using det_limit_side_len: {det_limit_side_len}")
    ocr_model1 = PaddleOCR(
        det_model_dir=None,
        rec_model_dir=None,
        use_angle_cls=False,
        det_limit_side_len=det_limit_side_len,
        det_limit_type='min',
        use_gpu=False,
        drop_score=0.5,
        det_db_box_thresh=0.5,
        det_db_unclip_ratio=2,
        use_dilation=False,
        det_box_type='quad'
    )    
    result = ocr_model1.ocr(processed_image, cls=True)
    text_list = [line[1][0] for line in result[0]]
    model = AutoModelForSequenceClassification.from_pretrained("model")

    tokenizer = AutoTokenizer.from_pretrained("model")

    clf = pipeline("text-classification", model=model, tokenizer=tokenizer)


    result1 = clf(text_list)
    label = result1[0]['label']
    lang_map= {
    'en': 'en',
    'fr': 'fr',
    'hi': 'hi',
    'zh': 'ch',
    'de': 'de',
    'ja': 'japan',
    'te': 'te',
    'es': 'es',
    'ar': 'ar',
    'ru': 'ru'
    }
    label2 = lang if lang else lang_map[label]
    print(label2)
    ocr_model2 = PaddleOCR(
        det_model_dir=None,
        rec_model_dir=None,
        use_angle_cls=False,
        lang=label2,
        det_limit_side_len=det_limit_side_len,
        det_limit_type='min',
        use_gpu=False,
        drop_score=0.5,
        det_db_box_thresh=0.5,
        det_db_unclip_ratio=2,
        use_dilation=False,
        det_box_type='quad'
        
    )



    print("🔍 Running combined OCR detection and recognition...")
    result2= ocr_model2.ocr(processed_image, cls=True)

    if not result2[0]:
        print("❌ No text regions detected.")
        return []

    # ✅ Apply filtering to remove small/irrelevant boxes
    filtered_result = filter_small_boxes(result2)

    if not filtered_result[0]:
        print("⚠️ All text boxes were filtered out.")
        return []

    # # 🖼️ Visualize the cleaned results
    visualize_with_labels(processed_image, filtered_result)

    # 📝 Extract final recognized texts
    final_results = []
    for line in filtered_result[0]:
        box = line[0]              # Coordinates of the bounding box
        text = line[1][0]          # Detected text
        score = line[1][1]         # Confidence score

        final_results.append({
            "text": text,
            "confidence": score,
            "coordinates": box
        })
        output_path = "detected_output_with_labels.jpg"
    return final_results, output_path