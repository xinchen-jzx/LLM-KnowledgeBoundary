import openai, time, json
import pandas as pd
import itertools

def generate(message, rounds):
    generations = []
    openai.api_key = "your key"
    messages = [
        {
            "role": "user",
            "content": message
        }
    ]
    for i in range(rounds):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        messages.append({'role':'system','content':response['choices'][0]['message']['content']})
        messages.append({'role':'user','content':'Tell me more questions.'})
        generations.append(response['choices'][0]['message']['content'])
    return generations

def generate_questions(sufix=''):
    with open('../data/prompt4questions.txt', 'r', encoding='utf8') as f:
        prompt = f.read()
    with open('../data/topics.txt', 'r', encoding='utf8') as f:
        topics = f.readlines()
    answer_dict = {}
    topics = [i.strip().lower() for i in topics]
    for index, topic in enumerate(topics):
        full_prompt = prompt.replace('xxxxx', topic)
        generations = generate(full_prompt, rounds=3)
        answer_dict[topic] = generations
        print(index, "/", len(topics))
    with open("../data/questions/full_questions.json", 'w') as json_file:
        json.dump(answer_dict, json_file)

#generate_questions(sufix='')