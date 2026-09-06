# WordLadder

A CLI SAT vocabulary quiz that tracks how well you know each word over time and actively re-tests you on your weak spots before you walk away.

The name comes from how words move: every word sits on one of three rungs, and each answer pushes it up or down the ladder.

## How it works

**The ladder**

Every word you've seen lives at one of three levels:

| Level | Description |
|---|---|
| `struggling` | you're missing this one more than you're getting it |
| `shaky` |getting there, but not solid yet |
| `known` | you've got it |

A correct answer moves a word **up** one rung. A wrong answer moves it **down** one rung. Levels floor out at `struggling` and cap out at `known` — no overflow either direction.

**Session quizzing**

Run the script and it asks you a random word with four multiple-choice definitions, same as before. Answer with `1`-`4`, or `q` any time to stop.

**The review round (on quit)**

This is the main addition. The moment you quit, instead of just printing a summary, WordLadder runs an **active recall round**:

1. It gathers every word you missed *this session*, plus every word in `progress.json` currently marked `struggling` or `shaky`.
2. It tosses in a couple of random `known` words too, just to keep them fresh.
3. It shuffles the whole pool and quizzes you on it, right then and there — updating levels live as you answer.
4. You can hit `q` again mid-review to bail out early if you're done.

Only after the review round finishes (or you quit out of it) does it print the final summary.

**Persistence**

Progress is saved to `progress.json` after every single answer, so nothing is lost if you close the terminal mid-session. Old `progress.json` files from before the ladder system existed are auto-migrated the first time you load them — your history isn't wiped, it's just translated into levels based on your past correct/incorrect counts.

## Running it

```bash
python quiz.py
```

Requires a `words.py` file in the same directory, defining a `words` dict of `{word: definition}` pairs.

## Files

| File | Purpose |
|---|---|
| `main.py` | The quiz itself |
| `words.py` | Your word list (generic SAT list included, BYOW though) |
| `progress.json` | Auto-created/updated; tracks level + correct/incorrect counts per word |

## Example summary output

```
Summary
Known well:      abrogate, laconic, sanguine
Still shaky on:  obdurate, perfidy
Needs review:    mendacious
```
