# pw_demo_sw_databank
Uses Playwright to screenshot and archive entries in the Star Wars Databank located at www.starwars.com/databank. It has two purposes - I'm a Star Wars fan and I want to make sure the entries on this site are archived in my collection, but it's also intended to reinforce and demo my knowledge of Playwright.

To run the script, simply issue the command:

uv run pytest

from the project directory. Screenshots are stored in the screenshots folder.

Todo:

--Make the number of entires a configurable parameter with --num_entries rather than hardcoded in test_databank.py. 