'''
mlu.tags.io

Author:   Nick Wrobel
Created:  2020-12-20
Modified: 2021-12-17


This module deals with reading tag and property values and album art of an audio file. 
Supports FLAC, Mp3, and M4A audio file types. 
'''

import logging

from mlu.tags.audiofmt import flac
from mlu.tags.audiofmt import mp3
from mlu.tags.audiofmt import m4a

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

logger = logging.getLogger("mluGlobalLogger")

SUPPORTED_AUDIO_TYPES = ['flac', 'mp3', 'm4a']

class AudioFileMetadataHandler:
    '''
    Class that reads data for a single audio file.

    Params:
        audioFilepath: absolute filepath of the audio file
    '''
    def __init__(self, audioFilepath):
        # validate that the filepath exists
        if (not mypycommons.file.isFile(audioFilepath)):
            raise ValueError("Class attribute 'audioFilepath' must be a valid filepath to an existing file: invalid value '{}'".format(audioFilepath))

        self.audioFilepath = audioFilepath

        # Strip the dot from the file extension to get the audio file type, used by this class
        self._audioFileType = mypycommons.file.getFileExtension(self.audioFilepath).replace('.', '')

        # Check that the given audio file type is supported
        if (self._audioFileType.lower() not in SUPPORTED_AUDIO_TYPES):
            raise Exception("Cannot open file '{}': Audio file format is not supported".format(self.audioFilepath))

        if (self._audioFileType == 'flac'):
            self._audioFmtHandler = flac.AudioFormatHandlerFLAC(self.audioFilepath)

        elif (self._audioFileType == 'mp3'):
            self._audioFmtHandler = mp3.AudioFormatHandlerMP3(self.audioFilepath)

        elif (self._audioFileType == 'm4a'):
            self._audioFmtHandler = m4a.AudioFormatHandlerM4A(self.audioFilepath)

    def getTags(self):
        '''
        Returns tags of the audio file
        '''
        return self._audioFmtHandler.getTags()

    def getProperties(self):
        '''
        Returns file properties of the audio file
        '''
        return self._audioFmtHandler.getProperties()

    def getEmbeddedArtwork(self):
        '''
        Returns the embedded artwork binary data of the audio file
        '''
        return self._audioFmtHandler.getEmbeddedArtwork()



    








 



     










    # def _setTagsForFLACFile(self, audioFileTags):
    #     '''
    #     Sets the FLAC file's tags to that of the AudioFileTags object given.
    #     '''
    #     mutagenInterface = mutagen.File(self.audioFilepath)

    #     mutagenInterface['title'] = audioFileTags.title
    #     mutagenInterface['artist'] = audioFileTags.artist
    #     mutagenInterface['album'] = audioFileTags.album
    #     mutagenInterface['albumartist'] = audioFileTags.albumArtist
    #     mutagenInterface['composer'] = audioFileTags.composer
    #     mutagenInterface['date'] = audioFileTags.date
    #     mutagenInterface['genre'] = audioFileTags.genre
    #     mutagenInterface['tracknumber'] = audioFileTags.trackNumber
    #     mutagenInterface['tracktotal'] = audioFileTags.totalTracks
    #     mutagenInterface['discnumber'] = audioFileTags.discNumber
    #     mutagenInterface['disctotal'] = audioFileTags.totalDiscs
    #     mutagenInterface['bpm'] = audioFileTags.bpm
    #     mutagenInterface['key'] = audioFileTags.key
    #     mutagenInterface['lyrics'] = audioFileTags.lyrics
    #     mutagenInterface['comment'] = audioFileTags.comment
    #     mutagenInterface['date_added'] = audioFileTags.dateAdded
    #     mutagenInterface['date_all_plays'] = audioFileTags.dateAllPlays
    #     mutagenInterface['date_last_played'] = audioFileTags.dateLastPlayed
    #     mutagenInterface['play_count'] = audioFileTags.playCount
    #     mutagenInterface['votes'] = audioFileTags.votes
    #     mutagenInterface['rating'] = audioFileTags.rating

    #     mutagenInterface.save()

    # def _setTagsForMp3File(self, audioFileTags):
    #     '''
    #     Sets the Mp3 file's tags to that of the AudioFileTags object given.
    #     '''
    #     # Use the EasyId3 interface for setting the standard Mp3 tags
    #     mutagenInterface = EasyID3(self.audioFilepath)

    #     mutagenInterface['title'] = audioFileTags.title
    #     mutagenInterface['artist'] = audioFileTags.artist
    #     mutagenInterface['album'] = audioFileTags.album
    #     mutagenInterface['albumartist'] = audioFileTags.albumArtist
    #     mutagenInterface['genre'] = audioFileTags.genre

    #     mutagenInterface.save()
        
    #     # Use the ID3 interface for setting the nonstandard Mp3 tags
    #     mutagenInterface = ID3(self.audioFilepath, v2_version=3)

    #     mutagenInterface['TXXX:DATE_ALL_PLAYS'] = TXXX(3, desc='DATE_ALL_PLAYS', text=audioFileTags.dateAllPlays)
    #     mutagenInterface['TXXX:DATE_LAST_PLAYED'] = TXXX(3, desc='DATE_LAST_PLAYED', text=audioFileTags.dateLastPlayed)
    #     mutagenInterface['TXXX:PLAY_COUNT'] = TXXX(3, desc='PLAY_COUNT', text=audioFileTags.playCount)
    #     mutagenInterface['TXXX:VOTES'] = TXXX(3, desc='VOTES', text=audioFileTags.votes)
    #     mutagenInterface['TXXX:RATING'] = TXXX(3, desc='RATING', text=audioFileTags.rating)

    #     mutagenInterface.save(v2_version=3)


    # def _setTagsForM4AFile(self, audioFileTags):
    #     '''
    #     Sets the M4A file's tags to that of the AudioFileTags object given.
    #     '''

    #     mutagenInterface = MP4(self.audioFilepath)

    #     # Standard M4A tags
    #     mutagenInterface['\xa9nam'] = audioFileTags.title
    #     mutagenInterface['\xa9ART'] = audioFileTags.artist
    #     mutagenInterface['\xa9alb'] = audioFileTags.album
    #     mutagenInterface['aART'] = audioFileTags.albumArtist
    #     mutagenInterface['\xa9gen'] = audioFileTags.genre

    #     # trackNumber, totalTracks, discNumber, and totalDiscs tags are not supported by MLU for
    #     # M4A files due to limitations of mutagen

    #     # Nonstandard (custom) M4A tags
    #     mutagenInterface['----:com.apple.iTunes:DATE_ALL_PLAYS'] = (audioFileTags.dateAllPlays).encode('utf-8')
    #     mutagenInterface['----:com.apple.iTunes:DATE_LAST_PLAYED'] = (audioFileTags.dateLastPlayed).encode('utf-8')
    #     mutagenInterface['----:com.apple.iTunes:PLAY_COUNT'] = (audioFileTags.playCount).encode('utf-8')
    #     mutagenInterface['----:com.apple.iTunes:VOTES'] = (audioFileTags.votes).encode('utf-8')
    #     mutagenInterface['----:com.apple.iTunes:RATING'] = (audioFileTags.rating).encode('utf-8')
