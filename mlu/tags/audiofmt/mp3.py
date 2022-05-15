'''
mlu.tags.audiofmt.mp3

Author:   Nick Wrobel
Created:  2021-12-11
Modified: 2021-12-17

Module containing class which reads data for a single mp3 audio file.
'''

import mutagen
from mutagen.mp3 import BitrateMode
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.convert

from mlu.tags import values

class AudioFormatHandlerMP3:
    def __init__(self, audioFilepath):
        self.audioFilepath = audioFilepath
        self.mutagenInterface = None

    def getEmbeddedArtwork(self):
        self.mutagenInterface = mutagen.File(self.audioFilepath)

        artworksData = []
        pictureTags = []
        mutagenTagKeys = list(self.mutagenInterface.keys())

        for tagKey in mutagenTagKeys:
            if ("APIC:" in tagKey):
                pictureTags.append(tagKey)

        for picTag in pictureTags:
            picData = self.mutagenInterface[picTag].data
            artworksData.append(picData)

        return artworksData

    def getProperties(self):
        self.mutagenInterface = mutagen.File(self.audioFilepath)

        fileSize = mypycommons.file.getFileSizeBytes(self.audioFilepath)
        fileDateModified = mypycommons.time.formatTimestampForDisplay(mypycommons.file.getFileDateModifiedTimestamp(self.audioFilepath))
        duration = self.mutagenInterface.info.length
        format = 'MP3'

        bitRateModeType = self.mutagenInterface.info.bitrate_mode
        if (bitRateModeType == BitrateMode.CBR):
            bitRateMode = 'CBR'
        elif (bitRateModeType == BitrateMode.VBR):
            bitRateMode = 'VBR'
        elif (bitRateModeType == BitrateMode.ABR):
            bitRateMode = 'ABR'
        else:
            bitRateMode = ''

        encoder = "{} ({})".format(self.mutagenInterface.info.encoder_info, self.mutagenInterface.info.encoder_settings)
        bitRate = mypycommons.convert.bitsToKilobits(self.mutagenInterface.info.bitrate)
        numChannels = self.mutagenInterface.info.channels
        sampleRate = self.mutagenInterface.info.sample_rate
        replayGain = {
            'albumGain': self._getTagValueFromMutagenInterface('TXXX:replaygain_album_gain'),
            'albumPeak': self._getTagValueFromMutagenInterface('TXXX:replaygain_album_peak'),
            'trackGain': self._getTagValueFromMutagenInterface('TXXX:replaygain_track_gain'),
            'trackPeak': self._getTagValueFromMutagenInterface('TXXX:replaygain_track_peak')
        }

        audioProperties = values.AudioFileProperties(
            fileSize=fileSize,
            fileDateModified=fileDateModified,
            duration=duration,
            format=format,
            bitRate=bitRate,
            sampleRate=sampleRate,
            numChannels=numChannels,
            replayGain=replayGain,
            bitDepth='',
            encoder=encoder,
            bitRateMode=bitRateMode,
            codec=''
        )
        return audioProperties

    def getTags(self):
        '''
        Returns an AudioFileTags object for the tag values for the Mp3 audio file
        '''
        title = self._getTagValueFromMutagenInterface('TIT2')
        artist = self._getTagValueFromMutagenInterface('TPE1')
        album = self._getTagValueFromMutagenInterface('TALB')
        albumArtist = self._getTagValueFromMutagenInterface('TPE2')
        genre = self._getTagValueFromMutagenInterface('TCON')
        bpm = self._getTagValueFromMutagenInterface('TBPM')
        date = self._getTagValueFromMutagenInterface('TDRC').text

        trackNumOfTotal = self._getTagValueFromMutagenInterface('TRCK')
        discNumOfTotal = self._getTagValueFromMutagenInterface('TPOS')

        if ('/' in trackNumOfTotal):
            parts = trackNumOfTotal.split('/')
            trackNumber = parts[0]
            totalTracks = parts[1]
        else:
            trackNumber = trackNumOfTotal
            totalTracks = ''

        if ('/' in discNumOfTotal):
            parts = discNumOfTotal.split('/')
            discNumber = parts[0]
            totalDiscs = parts[1]
        else:
            discNumber = discNumOfTotal
            totalDiscs = ''

        composer = self._getTagValueFromMutagenInterface('TCOM')
        key = self._getTagValueFromMutagenInterface('TXXX:Key')
        lyrics = self._getTagValueFromMutagenInterface('TXXX:LYRICS')
        comment = self._getTagValueFromMutagenInterface('COMM::eng')
        dateAdded = self._getTagValueFromMutagenInterface('TXXX:DATE_ADDED')
        dateAllPlays = self._getTagValueFromMutagenInterface('TXXX:DATE_ALL_PLAYS')
        dateLastPlayed = self._getTagValueFromMutagenInterface('TXXX:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterface('TXXX:PLAY_COUNT')
        votes = self._getTagValueFromMutagenInterface('TXXX:VOTES')
        rating = self._getTagValueFromMutagenInterface('TXXX:RATING')
        otherTags = {}

        tagFieldKeysMp3 = [
            'TIT2', 
            'TPE1', 
            'TALB', 
            'TPE2', 
            'TCOM', 
            'TDRC', 
            'TCON', 
            'TRCK', 
            'TPOS',
            'TBPM', 
            'TXXX:Key', 
            'TXXX:LYRICS', 
            'COMM::eng', 
            'TXXX:DATE_ADDED', 
            'TXXX:DATE_ALL_PLAYS', 
            'TXXX:DATE_LAST_PLAYED',
            'TXXX:PLAY_COUNT', 
            'TXXX:VOTES', 
            'TXXX:RATING'
        ]

        mutagenTagKeys = list(self.mutagenInterface.keys())
        relevantTagKeys = self._removeUnneededTagKeysFromTagKeysList(mutagenTagKeys)

        otherTagKeys = []
        for tagKey in relevantTagKeys:
            if (tagKey not in tagFieldKeysMp3):
                otherTagKeys.append(tagKey)

        for tagKey in otherTagKeys:
            tagValue = self._getTagValueFromMutagenInterface(tagKey)
            tagNameFormatted = self._formatMp3KeyToTagName(tagKey)
            otherTags[tagNameFormatted] = tagValue

        audioFileTags = values.AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            composer=composer,
            date=date,
            genre=genre, 
            trackNumber=trackNumber,
            totalTracks=totalTracks,
            discNumber=discNumber,
            totalDiscs=totalDiscs,
            bpm=bpm,
            key=key,
            lyrics=lyrics,
            comment=comment,
            dateAdded=dateAdded,
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            votes=votes, 
            rating=rating,
            OTHER_TAGS=otherTags
        )

        return audioFileTags

    def setTags(self, audioFileTags):
        '''
        '''
        # Use the EasyId3 interface for setting the standard Mp3 tags
        # mutagenInterface = EasyID3(self.audioFilepath)

        # mutagenInterface['title'] = audioFileTags.title
        # mutagenInterface['artist'] = audioFileTags.artist
        # mutagenInterface['album'] = audioFileTags.album
        # mutagenInterface['albumartist'] = audioFileTags.albumArtist
        # mutagenInterface['genre'] = audioFileTags.genre

        # mutagenInterface.save()
        
        # Use the ID3 interface for setting the nonstandard Mp3 tags
        mutagenInterface = ID3(self.audioFilepath, v2_version=3)

        mutagenInterface['TXXX:DATE_ALL_PLAYS'] = TXXX(3, desc='DATE_ALL_PLAYS', text=audioFileTags.dateAllPlays)
        mutagenInterface['TXXX:DATE_LAST_PLAYED'] = TXXX(3, desc='DATE_LAST_PLAYED', text=audioFileTags.dateLastPlayed)
        mutagenInterface['TXXX:PLAY_COUNT'] = TXXX(3, desc='PLAY_COUNT', text=audioFileTags.playCount)
        mutagenInterface['TXXX:VOTES'] = TXXX(3, desc='VOTES', text=audioFileTags.votes)
        mutagenInterface['TXXX:RATING'] = TXXX(3, desc='RATING', text=audioFileTags.rating)

        mutagenInterface.save(v2_version=3)

    def _removeUnneededTagKeysFromTagKeysList(self, mp3TagKeys):
        ignoreKeysMp3 = [
            'COMM:ID3v1 Comment:eng',
            'TXXX:replaygain_album_gain',
            'TXXX:replaygain_album_peak',
            'TXXX:replaygain_track_gain',
            'TXXX:replaygain_track_peak'
        ]

        relevantKeys = []
        for tagKey in mp3TagKeys:
            if ("APIC:" not in tagKey):
                relevantKeys.append(tagKey)

        for ignoreKey in ignoreKeysMp3:
            relevantKeys.remove(ignoreKey)

        return relevantKeys

    def _formatMp3KeyToTagName(self, mp3Key):
        if ("TXXX:" in mp3Key):
            tagName = mp3Key[5:]
        else:
            tagName = mp3Key

        return tagName.lower()

    def _getTagValueFromMutagenInterface(self, mutagenKey):
        try:
            mutagenValue = self.mutagenInterface[mutagenKey].text

            if (len(mutagenValue) == 1):
                tagValue = mutagenValue[0]
            elif (len(mutagenValue) > 1):
                tagValue = ';'.join(mutagenValue)
            else:
                tagValue = ''

        except KeyError:
            tagValue = ''

        return tagValue 
