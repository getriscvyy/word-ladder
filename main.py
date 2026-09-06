import random
import json
import os
from words import words

RELEASE = "0.2"

PROGRESS_FILE = "progress.json"
LEVELS = ["struggling", "shaky", "known"]

LEVEL_WEIGHTS = {
    "struggling": 5,
    "shaky": 3,
    "known": 1
}


def migrate_entry(entry):
    if "level" in entry:
        return entry

    correct = entry.get("correct", 0)
    incorrect = entry.get("incorrect", 0)

    if correct > 0 and incorrect == 0:
        level = "known"
    elif incorrect > correct:
        level = "struggling"
    elif correct > 0 and incorrect > 0:
        level = "shaky"
    else:
        level = "struggling"

    entry["level"] = level
    return entry


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            progress = json.load(f)
        for entry in progress.values():
            migrate_entry(entry)
        return progress
    return {}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def get_weighted_word_tuple(progress):
    word_list = list(words.keys())
    weights = []
    for w in word_list:
        entry = progress.get(w, {})
        lvl = entry.get("level", "struggling")
        weights.append(LEVEL_WEIGHTS.get(lvl, 5))
        
    selected_word = random.choices(word_list, weights=weights, k=1)[0]
    return selected_word, words[selected_word]


def get_choices(correct_word, correct_def):
    other_defs = [d for w, d in words.items() if w != correct_word]
    n = min(3, len(other_defs))
    distractors = random.sample(other_defs, n)
    choices = distractors + [correct_def]
    random.shuffle(choices)
    return choices


def level_up(entry):
    idx = LEVELS.index(entry.get("level", "struggling"))
    entry["level"] = LEVELS[min(idx + 1, len(LEVELS) - 1)]


def level_down(entry):
    idx = LEVELS.index(entry.get("level", "struggling"))
    entry["level"] = LEVELS[max(idx - 1, 0)]

def quiz_word(word, correct_def, progress, session_wrong=None):
    choices = get_choices(word, correct_def)
    print(f"\nWord: {word}")
    
    current_level = progress.get(word, {}).get("level", "struggling")
    print(f"Status: [{current_level.upper()}]")
    
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")

    selected = None
    skipped = False

    vim_map = {"h": 0, "j": 1, "k": 2, "l": 3}

    # Input loop: allows retry on typos, handles empty input as skipped, 'q' to quit
    while True:
        answer = input("Your answer (1-4, Enter to skip, or 'q' to quit): ").strip().lower()
        
        if answer == "q":
            return False
            
        if answer == "":
            print("Skipped.")
            skipped = True
            break

        if answer in vim_map:
            selected = choices[vim_map[answer]]
            break

        try:
            idx = int(answer) - 1
            if 0 <= idx < len(choices):
                selected = choices[idx]
                break
            else:
                print("Please select a valid option number (1-4).")
        except ValueError:
            print("Invalid input. Please enter a number from 1-4, press Enter to skip, or 'q' to quit.")

    entry = progress.setdefault(word, {"correct": 0, "incorrect": 0, "level": "struggling"})
    entry.setdefault("level", "struggling")

    if not skipped and selected == correct_def:
        print("Correct!")
        entry["correct"] += 1
        level_up(entry)
    else:
        if not skipped:
            print(f"Incorrect. The correct definition was: {correct_def}")
        else:
            print(f"The correct definition was: {correct_def}")
            
        entry["incorrect"] += 1
        level_down(entry)
        if session_wrong is not None:
            session_wrong.add(word)

    save_progress(progress)
    return True

def ask_question(progress, session_wrong):
    word, correct_def = get_weighted_word_tuple(progress)
    return quiz_word(word, correct_def, progress, session_wrong)


def review_round(progress, session_wrong):
    struggling = [w for w, e in progress.items() if e.get("level") == "struggling"]
    shaky = [w for w, e in progress.items() if e.get("level") == "shaky"]
    known = [w for w, e in progress.items() if e.get("level") == "known"]

    pool = set(session_wrong) | set(struggling) | set(shaky)
    pool = [w for w in pool if w in words]

    if known:
        extra = random.sample(known, min(2, len(known)))
        for w in extra:
            if w not in pool and w in words:
                pool.append(w)

    if not pool:
        return

    random.shuffle(pool)
    print("\n=== Review Round ===")
    print("Revisiting words you missed or need practice on:\n")

    for word in pool:
        correct_def = words[word]
        keep_going = quiz_word(word, correct_def, progress)
        if not keep_going:
            print("Ending review early.")
            break


def print_summary(progress):
    print("\n=== Summary ===")
    if not progress:
        print("No words attempted yet.")
        return

    known = sorted(w for w, s in progress.items() if s.get("level") == "known")
    shaky = sorted(w for w, s in progress.items() if s.get("level") == "shaky")
    struggling = sorted(w for w, s in progress.items() if s.get("level") == "struggling")

    print(f"Known well ({len(known)}):      {', '.join(known) if known else 'none yet'}")
    print(f"Still shaky on ({len(shaky)}):  {', '.join(shaky) if shaky else 'none'}")
    print(f"Needs review ({len(struggling)}):   {', '.join(struggling) if struggling else 'none'}")


if __name__ == "__main__":
    progress = load_progress()
    session_wrong = set()

    print("=== WordLadder CLI v" + RELEASE + " ===")
    print("Input 'q' at any time to quit.")

    while True:
        keep_going = ask_question(progress, session_wrong)
        if not keep_going:
            break

    review_round(progress, session_wrong)
    print_summary(progress)
    print(f"\nProgress saved to {PROGRESS_FILE}")

