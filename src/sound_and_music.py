import pygame
import sys

class SoundNMusicMixer:
    REPEAT_TRACK = -1
    SONG_END_EVENT = pygame.USEREVENT + 1

    def __init__(self):
        """ Initialize sound / music mixer class """
        self._sfxFiles = {}
        self._sfxVol = 1.0      # A value between 0.0 and 1.0
        self._musicFiles = {}   # Prefer .ogg for pygame (.mp3 is spotty on some platforms, e.g. Linux)
        self._musicVol = 1.0    # A value between 0.0 and 1.0
        self._musicPaused = 0

    def addSfxFileToMap(self, nameId, filePath):
        """Add sound effect file to internal mapping
        
           Note: This does not _load_ the files; only builds the internal mapping of which sound effects to load
        """
        # TODO: Consider either (A) loading all files at once (either here, or in a dedicated loader function), or (B) loading sound effects & unloading them as necessary (better for memory management?)
        # NOTE: How does one _unload_ sounds/music in Pygame? Documentation doesn't say.. The mixer class is a C class (or C++?) exposed to Python by a binding, so... basically, it's hidden.
        # Note: in Pygame, sound files are loaded as objects. You can store each object
        self._sfxFiles[nameId] = { 'path': filePath, 'obj': None }   # NOTE - this doesn't check for containment before updating the dict. Add it if you feel it's necessary

    def addMusicFileToMap(self, nameId, filePath):
        """Add music file to internal mapping
        
           Note: This does not _load_ the files; only builds the internal mapping of which sound effects to load
        """
        # Note: In Pygame, music files are streamed by the Pygame engine. We do not (and probably cannot) get the individual objects
        self._musicFiles[nameId] = filePath
    
    def setSfxVolume(self, volume):
        """Set SFX volume

           volume must be a float between 0.0 and 1.0, inclusive on both ends
           NOTE: In Pygame, sound effect volume is set per Sound object
        """
        # TODO consider having per-sound-effect volume mixer levels? Some sound effects might be louder than others.. Or otherwise, leave it to the sound guy to make sure the sound effect levels are good.. :-D
        # clamp volume levels
        if volume > 1.0:
            volume = 1.0
        elif volume < 0.0:
            volume = 0.0

        self._sfxVol = volume

        for _, sound in self._sfxFiles.iteritems():
            if sound['obj']:
                sound['obj'].set_volume(self._sfxVol)

    def setMusicVolume(self, volume):
        """Set Music volume

           volume must be a float between 0.0 and 1.0, inclusive on both ends
           NOTE: In Pygame, music volume is set at the mixer level (pygame.mixer.music.set_volume())
        """
        # clamp volume levels
        if volume > 1.0:
            volume = 1.0
        elif volume < 0.0:
            volume = 0.0

        self._musicVol = volume

        pygame.mixer.music.set_volume(self._musicVol)

    def loadSfxFiles(self):
        """Load sound files according to _sfxFiles map
           
           NOTE: Pygame does not check/prevent double-loading of the same file. You, the deevloper, must prevent that
        """
        # TODO maybe also write loadSfx(name) and unloadSfx(name). These can load/unload actual objects (memory management fun) <- dang.. probably not possible (see notes above)
        # TODO add exception handling here
        for nameId in self._sfxFiles:
            if not self._sfxFiles[nameId]['obj']: # prevent double-loading of sound objects
                self._sfxFiles[nameId]['obj'] = pygame.mixer.Sound(self._sfxFiles[nameId]['path'])

    def playSfx(self, engineRef=None, nameId=''):
        """Play a sound effect

           NOTE: We use kwargs here because the event queue/message system takes advantage of kwargs
           NOTE: We pass in engineRef because the application class calls this function, and the design calls for the application to pass a reference to itself to this function, in case we want/need it
        """
        #print "Playing sound {}".format(nameId)
        self._sfxFiles[nameId]['obj'].play()

    def loadMusicFile(self, nameId=''):
        """Load a music file _BY NAME ID_ (i.e. not by file name; we should have already specified the file name, using addMusicFileToMap)

           NOTE: Pygame streams music files (does not load the full file at once), so it is not necessary to prevent double-loading.
           But also NOTE: Pygame also supports loading multiple music files (using different syntax than I've used here, I believe.. Look into it)

           NOTE: We use kwargs here because the event queue/message system takes advantage of kwargs
        """
        # TODO add exception handling here
        pygame.mixer.music.load(self._musicFiles[nameId])

    def playMusic(self, engineRef=None, repeatMode=0):
        """Play loaded music file

           NOTE: Assumes a music file is already loaded
           NOTE: We pass in engineRef because the application class calls this function, and the design calls for the application to pass a reference to itself to this function, in case we want/need it
        """
        # TODO error checking -- what happens if we try to play music before loading a file? (use pygame.mixer.music.get_busy())
        pygame.mixer.music.play(repeatMode)

    def togglePauseMusic(self):
        """Pause loaded music file

           NOTE: Assumes a music file is already loaded
        """
        # TODO error checking -- what happens if we try to pause music if there is no music playing? (use pygame.mixer.music.get_busy())
        self._musicPaused = (self._musicPaused + 1) % 2

        if self._musicPaused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def stopMusic(self):
        """Stop loaded music file

           NOTE: Assumes a music file is already loaded
        """
        # TODO error checking -- what happens if we try to play music before loading a file? (use pygame.mixer.music.get_busy())
        pygame.mixer.music.stop()

