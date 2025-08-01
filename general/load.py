from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

def language_detection(text):

    model = AutoModelForSequenceClassification.from_pretrained("model")

    tokenizer = AutoTokenizer.from_pretrained("model")

    clf = pipeline("text-classification", model=model, tokenizer=tokenizer)

    result = clf(text)

    return result

if __name__ == "__main__":
    sample_text = "This is a sample text for language detection."
    result = language_detection(sample_text)
    print(f"Detected Language: {result[0]['label']} with score {result[0]['score']:.2f}")