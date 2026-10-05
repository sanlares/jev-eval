# Annotation brief: task C06

You are an expert human-quality annotator. For each text in `data/blind/C06.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: spoken commands to a smart-home voice assistant (transcribed)
- Question: "What does the user want the assistant to do?"
- Options:
- `lights_on`: Turn lights on
- `lights_off`: Turn lights off
- `dim_lights`: Change light brightness
- `set_thermostat`: Change or set the temperature
- `play_music`: Start playing music, a song, artist or playlist
- `pause_music`: Pause or stop music that is playing
- `volume_up`: Make it louder
- `volume_down`: Make it quieter
- `set_timer`: Start a countdown timer
- `set_alarm`: Set a wake-up or clock alarm
- `weather_query`: Ask about the weather or forecast
- `add_to_shopping_list`: Add an item to the shopping list
- `lock_door`: Lock a door
- `unlock_door`: Unlock a door
- `start_vacuum`: Start the robot vacuum
- `check_camera`: Show or check a security camera feed
- `call_contact`: Phone or video-call someone
- `read_calendar`: Ask about scheduled events or appointments
- `turn_on_tv`: Turn on the TV
- `other`: Anything not covered by the options above

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C06.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C06` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).
