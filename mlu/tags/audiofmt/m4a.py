'''
mlu.tags.audiofmt.m4a

Author:   Nick Wrobel
Created:  2021-12-11
Modified: 2021-12-17

Module containing class which reads data for a single m4a audio file.
'''

import mutagen
from mutagen.mp4 import MP4

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.convert

from mlu.tags import values

class AudioFormatHandlerM4A:
    def __init__(self, audioFilepath):
        self.audioFilepath = audioFilepath
        self.mutagenInterface = mutagen.File(audioFilepath)

    def getEmbeddedArtwork(self):
        '''
        '''        
        artworkData = []
        try:
            picsData = self.mutagenInterface.tags['covr']
            if (isinstance(picsData, list)):
                for picData in picsData:
                    artworkData.append(bytes(picData))
            
            else:
                artworkData.append(bytes(picsData))

            return artworkData

        except:
            return []

    def getProperties(self):
        '''
        '''
        fileSize = mypycommons.file.getFileSizeBytes(self.audioFilepath)
        fileDateModified = mypycommons.time.formatTimestampForDisplay(mypycommons.file.getFileDateModifiedTimestamp(self.audioFilepath))
        duration = self.mutagenInterface.info.length
        format = 'M4A'
        codec = self.mutagenInterface.info.codec_description
        bitRate = mypycommons.convert.bitsToKilobits(self.mutagenInterface.info.bitrate)
        bitDepth = self.mutagenInterface.info.bits_per_sample
        numChannels = self.mutagenInterface.info.channels
        sampleRate = self.mutagenInterface.info.sample_rate
        replayGain = {
            'albumGain': self._getTagValueFromMutagenInterface('----:com.apple.iTunes:replaygain_album_gain'),
            'albumPeak': self._getTagValueFromMutagenInterface('----:com.apple.iTunes:replaygain_album_peak'),
            'trackGain': self._getTagValueFromMutagenInterface('----:com.apple.iTunes:replaygain_track_gain'),
            'trackPeak': self._getTagValueFromMutagenInterface('----:com.apple.iTunes:replaygain_track_peak')
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
            bitDepth=bitDepth,
            encoder='',
            bitRateMode='',
            codec=codec
        )
        return audioProperties


    def getTags(self):
        '''
        Returns an AudioFileTags object for the tag values for the M4A audio file
        '''
        # Standard M4A tags
        title = self._getTagValueFromMutagenInterface('\xa9nam')
        artist = self._getTagValueFromMutagenInterface('\xa9ART')
        album = self._getTagValueFromMutagenInterface('\xa9alb')
        albumArtist = self._getTagValueFromMutagenInterface('aART')
        composer = self._getTagValueFromMutagenInterface('\xa9wrt')
        date = self._getTagValueFromMutagenInterface('\xa9day')
        genre = self._getTagValueFromMutagenInterface('\xa9gen')
        lyrics = self._getTagValueFromMutagenInterface('\xa9lyr')
        comment = self._getTagValueFromMutagenInterface('\xa9cmt')
        trackNumOfTotal = self._getTagValueFromMutagenInterface('trkn')
        discNumOfTotal = self._getTagValueFromMutagenInterface('disk')

        if (isinstance(trackNumOfTotal, tuple)):
            trackNumber = trackNumOfTotal[0]
            totalTracks = trackNumOfTotal[1]
            if (trackNumber == 0):
                trackNumber = ''
            if (totalTracks == 0):
                totalTracks = ''
        else:
            trackNumber = ''
            totalTracks = ''

        if (isinstance(discNumOfTotal, tuple)):
            discNumber = discNumOfTotal[0]
            totalDiscs = discNumOfTotal[1]
            if (discNumber == 0):
                discNumber = ''
            if (totalDiscs == 0):
                totalDiscs = ''
        else:
            discNumber = ''
            totalDiscs = ''
        

        # Nonstandard (custom) M4A tags
        key = self._getTagValueFromMutagenInterface('----:com.apple.iTunes:key')
        bpm = self._getTagValueFromMutagenInterface('----:com.apple.iTunes:BPM')
        dateAdded = self._getTagValueFromMutagenInterface('----:com.apple.iTunes:DATE_ADDED')
        dateAllPlays = self._getTagValueFromMutagenInterface('----:com.apple.iTunes:DATE_ALL_PLAYS')
        dateLastPlayed = self._getTagValueFromMutagenInterface('----:com.apple.iTunes:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterface('----:com.apple.iTunes:PLAY_COUNT')
        votes = self._getTagValueFromMutagenInterface('----:com.apple.iTunes:VOTES')
        rating = self._getTagValueFromMutagenInterface('----:com.apple.iTunes:RATING')
        otherTags = {}

        tagFieldKeysM4A = [
            '\xa9nam', 
            '\xa9ART',
            '\xa9alb', 
            'aART', 
            '\xa9wrt', 
            '\xa9day', 
            '\xa9gen', 
            '\xa9lyr', 
            '\xa9cmt',
            'trkn', 
            'disk', 
            '----:com.apple.iTunes:key', 
            '----:com.apple.iTunes:BPM', 
            '----:com.apple.iTunes:DATE_ADDED', 
            '----:com.apple.iTunes:DATE_ALL_PLAYS', 
            '----:com.apple.iTunes:DATE_LAST_PLAYED',
            '----:com.apple.iTunes:PLAY_COUNT', 
            '----:com.apple.iTunes:VOTES', 
            '----:com.apple.iTunes:RATING'
        ]

        mutagenTagKeys = list(self.mutagenInterface.keys())
        relevantTagKeys = self._removeUnneededTagKeysFromTagKeysList(mutagenTagKeys)

        otherTagKeys = []
        for tagKey in relevantTagKeys:
            if (tagKey not in tagFieldKeysM4A):
                otherTagKeys.append(tagKey)

        for tagKey in otherTagKeys:
            tagValue = self._getTagValueFromMutagenInterface(tagKey)
            tagNameFormatted = self._formatM4AKeyToTagName(tagKey)
            otherTags[tagNameFormatted] = tagValue

        audioFileTags = values.AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            composer=composer,
            date=date,
            genre=genre, 
            trackNumber=str(trackNumber),
            totalTracks=str(totalTracks),
            discNumber=str(discNumber),
            totalDiscs=str(totalDiscs),
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

    def _removeUnneededTagKeysFromTagKeysList(self, m4aKeys):
        keysToRemove = [
            'covr',
            '----:com.apple.iTunes:replaygain_album_gain',
            '----:com.apple.iTunes:replaygain_album_peak',
            '----:com.apple.iTunes:replaygain_track_gain',
            '----:com.apple.iTunes:replaygain_track_peak',
            'itunsmpb',
            'itunnorm'
        ]

        for removeKey in keysToRemove:
            try:
                m4aKeys.remove(removeKey)
            except:
                pass

        return m4aKeys

    def _formatM4AKeyToTagName(self, m4aKey):
        if ("----:com.apple.iTunes:" in m4aKey):
            tagName = m4aKey[22:]
        else:
            tagName = m4aKey

        return tagName.lower()

    def _getTagValueFromMutagenInterface(self, mutagenKey):

        try:    
            mutagenValue = self.mutagenInterface.tags[mutagenKey]

            if ('----:com.apple.iTunes:' in mutagenKey):
                if (len(mutagenValue) == 1):
                    tagValue = mutagenValue[0].decode('utf-8')
                elif (len(mutagenValue) > 1):
                    tagValueList = [value.decode('utf-8') for value in mutagenValue]
                    tagValue = ';'.join(tagValueList)
                else:
                    tagValue = ''

            else:
                if (len(mutagenValue) == 1):
                    tagValue = mutagenValue[0]
                elif (len(mutagenValue) > 1):
                    tagValue = ';'.join(mutagenValue)
                else:
                    tagValue = ''

        except KeyError:
            tagValue = ''

        return tagValue