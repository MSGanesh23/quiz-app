import json
import re
import os

def parse_format_b(content):
    """Parses Moodle format (co3.txt, co4.txt)"""
    # Split by "Question [0-9]+"
    raw_questions = re.split(r'Question \d+CorrectMark \d\.\d+ out of \d\.\d+Flag question', content)
    
    questions = []
    for raw in raw_questions:
        if not raw.strip():
            continue
            
        lines = [line.strip() for line in raw.strip().split('\n') if line.strip()]
        
        if not lines:
            continue
            
        question_text = ""
        options = []
        correct_answer = ""
        
        # Find index of "a."
        try:
            a_index = -1
            for i, line in enumerate(lines):
                if line.lower() == 'a.':
                    a_index = i
                    break
            
            if a_index == -1:
                continue
                
            question_text = " ".join(lines[1:a_index]).replace('Question text', '').strip()
            
            # Extract options
            current_option_label = ""
            current_option_text = ""
            
            i = a_index
            while i < len(lines):
                line = lines[i]
                if line.lower() in ['a.', 'b.', 'c.', 'd.', 'e.']:
                    if current_option_label:
                        options.append({'label': current_option_label, 'text': current_option_text.strip()})
                    current_option_label = line[0]
                    current_option_text = ""
                elif line == "Correct":
                    pass 
                elif line == "Feedback":
                    if current_option_label:
                        options.append({'label': current_option_label, 'text': current_option_text.strip()})
                        current_option_label = ""
                    break
                else:
                    current_option_text += " " + line
                i += 1
            
            # Find correct answer
            for line in lines:
                if "The correct answer is:" in line:
                    correct_answer = line.replace("The correct answer is:", "").strip()
                    break
            
            if question_text and options and correct_answer:
                questions.append({
                    'question': question_text,
                    'options': options,
                    'answer': correct_answer
                })
        except Exception as e:
            print(f"Error parsing question: {e}")
            continue
            
    return questions

def parse_format_a(content):
    """Parses standard format (co1.txt)"""
    # Split by Q[number].
    raw_questions = re.split(r'Q\d+\.', content)
    
    questions = []
    for raw in raw_questions:
        if not raw.strip():
            continue
            
        lines = [line.strip() for line in raw.strip().split('\n') if line.strip()]
        
        if not lines:
            continue
            
        question_text = ""
        options = []
        correct_answer = ""
        correct_label = ""
        
        try:
            a_index = -1
            for i, line in enumerate(lines):
                if line.lower().startswith('a)'):
                    a_index = i
                    break
            
            if a_index == -1:
                continue
                
            question_text = " ".join(lines[0:a_index]).strip()
            
            # Extract options
            current_option_label = ""
            current_option_text = ""
            
            i = a_index
            while i < len(lines):
                line = lines[i]
                if re.match(r'^[a-e]\)', line.lower()):
                    if current_option_label:
                        options.append({'label': current_option_label, 'text': current_option_text.strip()})
                    current_option_label = line[0]
                    current_option_text = line[2:].strip()
                elif line.startswith("Correct Answer:"):
                    if current_option_label:
                        options.append({'label': current_option_label, 'text': current_option_text.strip()})
                        current_option_label = ""
                    correct_label = line.replace("Correct Answer:", "").strip().lower()
                    break
                else:
                    current_option_text += " " + line
                i += 1
            
            if correct_label:
                for opt in options:
                    if opt['label'] == correct_label:
                        correct_answer = opt['text']
                        break
            
            if question_text and options and correct_answer:
                questions.append({
                    'question': question_text,
                    'options': options,
                    'answer': correct_answer
                })
        except Exception as e:
            print(f"Error parsing question: {e}")
            continue
            
    return questions

def parse_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "CorrectMark" in content:
        print(f"Using Strategy B (Moodle) for {file_path}")
        return parse_format_b(content)
    else:
        print(f"Using Strategy A (Standard) for {file_path}")
        return parse_format_a(content)

if __name__ == "__main__":
    files = ['co1.txt', 'co3.txt', 'co4.txt']
    grand_quiz = []
    
    for file in files:
        if os.path.exists(file):
            qs = parse_file(file)
            print(f"Parsed {len(qs)} questions from {file}")
            
            out_file = file.replace('.txt', '.json')
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(qs, f, indent=2)
            
            grand_quiz.extend(qs)
        else:
            print(f"File {file} not found.")
            
    with open('grand_quiz.json', 'w', encoding='utf-8') as f:
        json.dump(grand_quiz, f, indent=2)
    print(f"Parsed total {len(grand_quiz)} questions for Grand Quiz.")
