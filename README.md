# Falldown Low Rez
Mass KonFuzion Games presents Falldown Low Rez, a re-imagining of [Falldown, the TI calculator game](https://www.youtube.com/watch?v=aIAx7kjb9Gg), in low-resolution. Oh wait, Falldown was low-resolution to begin with. Hmm....
This game was my submission for [Low Rez Jam 2016](https://itch.io/jam/lowrezjam2016).

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
Binaries aren't available on GitHub yet. Once the game is a bit more complete, I will also make available stand-alone binary packages (no installation necessary; just unpack and play)

## Some Other Notes
* Falldown is kinda incomplete...
  * The game was a rush job; I wanted to get _something_ working in time to submit for the Low Rez Jam.
  * I am finishing it and cleaning it up (basically, I'm saying the game is incomplete. Don't judge :-D)
  * The code is sloppy in some parts. I'm working to fix that
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
