import random
import json
import os
from words import words

RELEASE = "0.1"

PROGRESS_FILE = "progress.json"
# Levels go from worst to best. A correct answer moves a word one level up,
# an incorrect answer moves it one level down (floor/ceiling at the ends).
LEVELS = ["struggling", "shaky", "known"]


def migrate_entry(entry):
    # Add a 'level' field to older progress entries that don't have one yet,
    # inferring it from their correct/incorrect counts.
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


def get_word_tuple():
    return random.choice(list(words.items()))


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
    # Ask about a single word. Returns False if the user quit, True otherwise.
    choices = get_choices(word, correct_def)
    print(f"\nWord: {word}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")

    answer = input("Your answer (1-4, or 'q' to quit): ").strip()
    if answer.lower() == "q":
        return False

    try:
        idx = int(answer) - 1
        selected = choices[idx]
    except (ValueError, IndexError):
        print("Invalid input — counting that as incorrect.")
        selected = None

    entry = progress.setdefault(word, {"correct": 0, "incorrect": 0, "level": "struggling"})
    entry.setdefault("level", "struggling")

    if selected == correct_def:
        print("Correct!")
        entry["correct"] += 1
        level_up(entry)
    else:
        print(f"Incorrect. The correct definition was: {correct_def}")
        entry["incorrect"] += 1
        level_down(entry)
        if session_wrong is not None:
            session_wrong.add(word)

    save_progress(progress)
    return True


def ask_question(progress, session_wrong):
    word, correct_def = get_word_tuple()
    return quiz_word(word, correct_def, progress, session_wrong)


def review_round(progress, session_wrong):
    # On quit, actively re-quiz on this session's misses plus anything struggling or shaky in progress.json.
    # Add a couple of known words mixed in for good measure.
    struggling = [w for w, e in progress.items() if e.get("level") == "struggling"]
    shaky = [w for w, e in progress.items() if e.get("level") == "shaky"]
    known = [w for w, e in progress.items() if e.get("level") == "known"]

    pool = set(session_wrong) | set(struggling) | set(shaky)
    pool = [w for w in pool if w in words]  # guard against stale words no longer in the list

    if known:
        extra = random.sample(known, min(2, len(known)))
        for w in extra:
            if w not in pool and w in words:
                pool.append(w)

    if not pool:
        return

    random.shuffle(pool)
    print("\n===Review Round===")
    print("Revisiting words you've missed or are still shaky on, plus a couple you know well.\n")

    for word in pool:
        correct_def = words[word]
        keep_going = quiz_word(word, correct_def, progress)
        if not keep_going:
            print("Ending review early.")
            break


def print_summary(progress):
    print("\n===Summary===")
    if not progress:
        print("No words attempted yet.")
        return

    known = sorted(w for w, s in progress.items() if s.get("level") == "known")
    shaky = sorted(w for w, s in progress.items() if s.get("level") == "shaky")
    struggling = sorted(w for w, s in progress.items() if s.get("level") == "struggling")

    print(f"Known well:      {', '.join(known) if known else 'none yet'}")
    print(f"Still shaky on:  {', '.join(shaky) if shaky else 'none'}")
    print(f"Needs review:    {', '.join(struggling) if struggling else 'none'}")


if __name__ == "__main__":
    progress = load_progress()
    session_wrong = set()

    print("===WordLadder CLI v" + RELEASE + "===")
    print("Input 'q' at any time to quit.")

    while True:
        keep_going = ask_question(progress, session_wrong)
        if not keep_going:
            break

    review_round(progress, session_wrong)
    print_summary(progress)
    print(f"\nProgress saved to {PROGRESS_FILE}")

