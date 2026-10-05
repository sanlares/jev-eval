# Generation brief: task C06

You are writing synthetic **evaluation items** for a text classifier. Every item has a PRE-ASSIGNED
ground-truth label. Your job is to write the text so that a careful expert would assign exactly that label.

## The task
- Domain: spoken commands to a smart-home voice assistant (transcribed)
- Question that will be asked about each text: "What does the user want the assistant to do?"
- Label values (as they appear in the plan) and their meaning:
- `"lights_on"` → Turn lights on
- `"lights_off"` → Turn lights off
- `"dim_lights"` → Change light brightness
- `"set_thermostat"` → Change or set the temperature
- `"play_music"` → Start playing music, a song, artist or playlist
- `"pause_music"` → Pause or stop music that is playing
- `"volume_up"` → Make it louder
- `"volume_down"` → Make it quieter
- `"set_timer"` → Start a countdown timer
- `"set_alarm"` → Set a wake-up or clock alarm
- `"weather_query"` → Ask about the weather or forecast
- `"add_to_shopping_list"` → Add an item to the shopping list
- `"lock_door"` → Lock a door
- `"unlock_door"` → Unlock a door
- `"start_vacuum"` → Start the robot vacuum
- `"check_camera"` → Show or check a security camera feed
- `"call_contact"` → Phone or video-call someone
- `"read_calendar"` → Ask about scheduled events or appointments
- `"turn_on_tv"` → Turn on the TV
- `"other"` → Anything not covered by the options above
- Task-specific notes: Commands sound like natural speech. Implicit: 'it's pitch black in here' -> lights_on. Distractor: 'once this song ends, wake me at 7' -> set_alarm. Negation: 'don't turn them off, just lower them' -> dim_lights. 'other' items are requests outside the list (order food, trivia, jokes, reminders to email someone...).

## Plan
`data/plan/C06.jsonl` has 70 rows. Each row fixes: `label`, `difficulty`, `hard_type`, `length`,
`subtopic` (the situation to write about; invent everything else) and `writer` (persona/style; may be null).

Difficulty:
- **easy**: The label is obvious: explicit, typical cues that any reader would recognise.
- **medium**: The label must be inferred from context. Avoid the most obvious keywords and never use the label name itself.
- **hard**: Hard case of the row's hard_type (see 'Hard types' below). The label must STILL be unambiguous to a careful expert reader.

Hard types used in this task:
- **distractor**: Prominently mention a cue that belongs to a different label, but make the correct label clearly the main point.
- **implicit**: No explicit keywords at all; the label is only inferable from indirect, concrete details.
- **negation**: Use negation or an explicit denial to flip a surface cue (the text mentions X, but says it is not the case / not wanted).

Length:
- **medium**: 3-6 sentences (~50-120 words).
- **short**: 1-2 sentences (at most ~40 words).

## Hard rules
1. The assigned label must be clearly the best answer for a careful expert, including hard items. Hard means
   "requires care", never "ambiguous". If a hard_type would make the item ambiguous, adjust it until it isn't.
2. In medium and hard items never use the label name or copy the label description. Never add meta-commentary
   about the label (e.g. "this is a billing issue").
3. Everything is fictional: invent names, companies, places, numbers. No real people, brands or tickers.
4. English only. Make every item distinct: vary names, openings, structure and details; do not reuse templates.
5. The `state` of each item is a plain string.

## Output
Write `data/raw/C06.jsonl` with one JSON object per line, `{"id": ..., "state": ...}`, for EVERY plan row, in
plan order. Work in batches of about 15 items: after each batch, APPEND its lines to the file with a small python3
script using `json.dumps` (avoids escaping errors), so progress is saved. If the file already exists when you start,
keep the items in it and continue from the first plan id that is missing. When all rows are written, run
`python3 build.py check-raw C06` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.
