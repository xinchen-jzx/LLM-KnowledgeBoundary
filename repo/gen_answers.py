import openai, time, json, re
import os
import pickle
from utils import *

def format_answers(answers):
    all_matches = []
    for answer in answers:
        lines = answer.split("\n")
        matches = []
        for line in lines:
            match = re.search(r'\b\d+\.\s\"(.+?)\"', line)
            if match:
                matches.append(match.group(1))
            else:
                matches += [i[1] for i in re.findall(r'\b\d+\.\s(?:\"(.+?)\"|\s?(.+?))(?:\s\(.*\)|\s\u2013|-|:\s?|\n|$)', line)]

        all_matches+=matches
        #print(matches)
        #matches = re.findall(r'\b\d\.\s([\w\s\-]+)(?:\s\(.*\)|:)', answer)
        #matches += clean_keywords(answer)
        #matches += re.findall(r'(\d+\.\s(.*?)(?:\s–|:|\n| \())|"(.*)"', answer)
        #matches += re.findall(r'\b\d+\.\s(.+?)(?:\s\(.*\)|\s\u2013|-|:\s?|\n)', answer)
        #print(matches)
    return all_matches


if os.path.isfile('../data/answers/save_state/save_state.pkl'):
    with open('../data/answers/save_state/save_state.pkl', 'rb') as f:
        list_answers, counter = pickle.load(f)
else:
    list_answers = []
    counter = 0

def gen_answer():
    with open('../data/questions/questions.json', 'r') as f:
        questions_list = json.load(f)

    # 创建状态保存目录
    if not os.path.exists('../data/answers/save_state'):
        os.mkdir('../data/answers/save_state')

    def exception_handler(func):
        global counter

        def wrapper(*args, **kwargs):
            global counter

            if counter % 10 == 0:  # 每个X次,保存一次
                print(counter)
                with open('../data/answers/save_state/save_state.pkl', 'wb') as f:
                    pickle.dump((list_answers, counter), f)
                with open('../data/answers/answers_temp.json', 'w') as f:
                    json.dump(list_answers, f)
            counter += 1
            try:
                return func(*args, **kwargs)
            except Exception:
                print("发生了异常，断点位置为: ", counter)
                return None

        return wrapper

    @exception_handler
    def extend_question_dict(question_dict):
        question = question_dict["question"]
        answer = generate(question, rounds=1)
        question_dict["answer"] = answer
        question_dict["answer_entities"] = format_answers(answer)
        return question_dict


    if os.path.isfile('../data/answers/save_state/save_state.pkl'):
        with open('../data/answers/save_state/save_state.pkl', 'rb') as f:
            list_answers, counter = pickle.load(f)
    else:
        list_answers = []
        counter = 0


    for question_dict in questions_list[counter:]:
        new_question_dict = {'question':question_dict['question']}
        new_question_dict = extend_question_dict(new_question_dict)
        if new_question_dict is not None:
            list_answers.append(new_question_dict)
        if counter == 3:
            break


    with open('../data/answers/init_answers.json', 'w') as f:
        json.dump(list_answers, f)

def gen_remaining_answer():
    full_answer_list = []
    with open('../data/questions/questions.json', 'r') as f:
        questions_list = json.load(f)
    with open('../data/answers/init_answers.json', 'r') as f:
        answers_list = json.load(f)
    i = 0
    count = 0
    for item in questions_list:
        if item['question'] == answers_list[i]['question']:
            temp_dict = answers_list[i]
            temp_dict["answer_entities"] = format_answers(temp_dict["answer"])
            full_answer_list.append(temp_dict)
            i+=1
        else:
            count+=1
            print(count)
            question = item['question']
            answer = generate(question, rounds=3) 
            item["answer"] = answer
            item["answer_entities"] = format_answers(answer)
            full_answer_list.append(item)
    print(len(answers_list))
    print(len(questions_list))
    print(len(full_answer_list))
    with open('../data/answers/final_answers.json', 'w') as f:
        json.dump(full_answer_list, f)

gen_answer()
gen_remaining_answer()