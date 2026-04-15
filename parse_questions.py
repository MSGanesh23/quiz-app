import json
import re

def parse_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by "Question [0-9]+"
    raw_questions = re.split(r'Question \d+CorrectMark \d\.\d+ out of \d\.\d+Flag question', content)
    
    questions = []
    for raw in raw_questions:
        if not raw.strip():
            continue
            
        lines = [line.strip() for line in raw.strip().split('\n') if line.strip()]
        
        if not lines:
            continue
            
        # Lines 0 is usually "Question text"
        # Line 1 is the actual question content (might span multiple lines)
        
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
                
            question_text = " ".join(lines[1:a_index])
            
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
                    pass # Handled by finding "The correct answer is:"
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

if __name__ == "__main__":
    qs = parse_questions('questions.txt')
    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(qs, f, indent=2)
    print(f"Parsed {len(qs)} questions.")
