# WordLadder
a cli vocabulary quiz that tracks how well you know each word over time and actively re-tests you on your weak spots before you walk away.

## overview
the name comes from how words move: every word sits on one of three rungs, and each answer pushes it up or down the ladder.

## the ladder
every word you've seen lives at one of three levels:
| Level | Description |
|---|---|
| `struggling` | you're missing this one more than you're getting it |
| `shaky` | getting there, but not solid yet |
| `known` | you've got it |

a correct answer moves a word **up** one rung. a wrong answer moves it **down** one rung. levels floor out at `struggling` and cap out at `known`.

## how it works
### session quizzing
run the script and it asks you a random word with four multiple-choice definitions. answer with `1`-`4`, or `q` any time to stop.
### the review round (on quit)

the moment you quit, instead of just printing a summary, WordLadder runs an **active recall round**:
| Step | Action |
|---|---|
| 1 | gathers every word you missed this session, plus every word in `progress.json` currently marked `struggling` or `shaky` |
| 2 | tosses in a couple of random `known` words too, just to keep them fresh |
| 3 | shuffles the whole pool and quizzes you on it, right then and there — updating levels live as you answer |
| 4 | you can hit `q` again mid-review to bail out early if you're done |

only after the review round finishes (or you quit out of it) does it print the final summary.
### persistence

progress is saved to `progress.json` after every single answer, so nothing is lost if you close the terminal mid-session. old `progress.json` files from before the ladder system existed are auto-migrated the first time you load them — your history isn't wiped, it's just translated into levels based on your past correct/incorrect counts.
## running it
```bash
python main.py
```
requires a `words.py` file in the same directory, defining a `words` dict of `{word: definition}` pairs.

## files
| File | Purpose |
|---|---|
| `main.py` | the quiz itself |
| `words.py` | your word list (generic SAT list included, BYOW though) |
| `progress.json` | auto-created/updated; tracks level + correct/incorrect counts per word |

## example summary output
```
Summary
Known well:      abrogate, laconic, sanguine
Still shaky on:  obdurate, perfidy
Needs review:    mendacious
```
