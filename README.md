# Falldown x64
Mass KonFuzion Games presents Falldown x64, a re-imagining of [Falldown, the TI calculator game](https://www.youtube.com/watch?v=aIAx7kjb9Gg), in low-resolution. Oh wait, Falldown was low-resolution to begin with. Hmm....
This game was [my submission](https://masskonfuzion.itch.io/falldown-x64) for [Low Rez Jam 2016](https://itch.io/jam/lowrezjam2016).

## Installing and Running Falldown
Falldown doesn't get "installed" per se; it is programmed in Python 2, so [if you don't already have Python 2, you'll need to get it](https://www.python.org/downloads/). **Note:** Get Python _2_, not Python _3_. Well, you can get Python 3 if you want it; it's great. But it won't run Falldown.

To run Falldown:

**Linux/Mac**
```sh
cd src
./falldown.py
```
*NOTE* The "#!" line in falldown.py reflects the python binary location on my development laptop (/usr/bin/python2). If your python binary is different than mine, you can either modify falldown.py to correct the "#!", or run it as:
```sh
cd src
<your python binary> falldown.py
```

**Windows**
```sh
cd src
python falldown.py
```
*NOTE* The above assumes that path to the Python executable is in your PATH environment variable. If it's not, you can add it, or otherwise give the full path to the python binary (likely C:\Python27\python.exe)

## External Dependencies
Falldown depends on the following Python modules:
* [Pygame](http://www.pygame.org/download.shtml)
* Nothing else at the moment, but this dependencies list could grow, as I continue to develop Falldown.

Yes, I know that Pygame is a bit outdated. But it's still functional, easy, and familiar to me. (Low Rez Jam lasted 2 weeks, and I needed to be able to make a game from scratch in that time frame).

## What About Binaries?
Binaries are available at https://masskonfuzion.itch.io/falldown-x64.  Note that the binary releases may (read: likely will) lag behind the source snapshots.

## Some Other Notes
* Is this game any good? Or fun?
  * Truthfully, no, not really :-D The difficulty curve is crap. This is very much a learning, "stepping-stone" project. The goal of this project was for me to make "the things a game should have". That includes:
    * The engine/brains/guts
    * Game states (playing game, paused, etc.)
    * Menus (settings, high scores, instructions, credits, etc.)
    * Music, sound effects
    * Some visual effects (hmm.. There are no VFX yet)
    * Some semblance of a difficulty curve
    * etc.
  * To the end of making a finished game, Falldown is a major success
    * Sure, there are some known loose ends and rough edges...
    * But for a 100% hand-crafted-everything project, I am happy that I made a working game
    * And, I'm happy that I was able to structure a flexible codebase that expands gracefully and supports whatever features I think of
    * (Trust me, it has taken several tries at making games to get to this point)
    * If I find inspiration, I will tweak the game to have a more robust difficulty curve
* The version of Falldown that's available here, on GitHub, will likely be more up-to-date than what's available on itch.io


## Legal Stuff
Copyright 2016 Mass KonFuzion Games

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
