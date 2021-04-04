from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-distilled-squad")

model = AutoModelForQuestionAnswering.from_pretrained(
    "distilbert-base-uncased-distilled-squad"
)

qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)


def extract_item_loc(sentence: str):
    item = qa_pipeline(question="What is the item?", context=sentence)["answer"]
    location = qa_pipeline(question=f"Where is {item}?", context=sentence)["answer"]

    return item, location


while True:
    item, location = extract_item_loc(input("Enter a sentence: "))
    print(f"Item: {item}, Location: {location}")
