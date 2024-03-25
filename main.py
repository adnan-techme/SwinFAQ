import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
import csv
from fuzzywuzzy import process


def load_faq_data(csv_filename):
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None) 
        faq_data = [{"question": row[0], "answer": row[1]} for row in reader]
    return faq_data

def find_relevant_faqs(question, faq_data, num_faqs=5):
    scores = [(faq, process.fuzz.partial_ratio(question.lower(), faq["question"].lower())) for faq in faq_data]
    sorted_faqs = sorted(scores, key=lambda x: x[1], reverse=True)[:num_faqs]
    relevant_faqs = [faq[0] for faq in sorted_faqs if faq[1] > 50]  
    return relevant_faqs

def ask_openai_with_context(question, faq_data):
    relevant_faqs = find_relevant_faqs(question, faq_data)
    messages = [{"role": "system", "content": "You are a helpful assistant knowledgeable about queries regarding Swinburne University of Technology"}]
    messages += [{"role": "user", "content": faq["question"], "role": "assistant", "content": faq["answer"]} for faq in relevant_faqs]
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.5,
    max_tokens=150,
    stop=None)
    
    return response.choices[0].message.content

faq_data = load_faq_data('data.csv')
user_question = input("Please ask a question: ")
answer = ask_openai_with_context(user_question, faq_data)
print(f"Answer: {answer}")
