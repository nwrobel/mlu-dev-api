'''
mlu.tags.audiofmt.flac

Author:   Nick Wrobel
Created:  2021-12-11
Modified: 2021-12-17

Module containing class which reads data for a single FLAC audio file.
'''

import mutagen

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.convert

from mlu.tags import values

class AudioFormatHandlerFLAC:
    def __init__(self, audioFilepath):
        self.audioFilepath = audioFilepath
        self.mutagenInterface = None

    def getEmbeddedArtwork(self):
        '''
        '''
        self.mutagenInterface = mutagen.File(self.audioFilepath)

        artworksData = []
        for picture in self.mutagenInterface.pictures:
            artworksData.append(picture.data)
        
        return artworksData 

    def getProperties(self):
        '''
        '''
        self.mutagenInterface = mutagen.File(self.audioFilepath)

        fileSize = mypycommons.file.getFileSizeBytes(self.audioFilepath)
        fileDateModified = mypycommons.time.formatTimestampForDisplay(mypycommons.file.getFileDateModifiedTimestamp(self.audioFilepath))
        duration = self.mutagenInterface.info.length
        format = 'FLAC'
        bitRate = mypycommons.convert.bitsToKilobits(self.mutagenInterface.info.bitrate)
        bitDepth = self.mutagenInterface.info.bits_per_sample
        numChannels = self.mutagenInterface.info.channels
        sampleRate = self.mutagenInterface.info.sample_rate
        replayGain = {
            'albumGain': self._getTagValueFromMutagenInterface('replaygain_album_gain'),
            'albumPeak': self._getTagValueFromMutagenInterface('replaygain_album_peak'),
            'trackGain': self._getTagValueFromMutagenInterface('replaygain_track_gain'),
            'trackPeak': self._getTagValueFromMutagenInterface('replaygain_track_peak')
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
            codec=''
        )
        return audioProperties



    def getTags(self):
        '''
        Returns an AudioFileTags object for the tag values for the FLAC audio file
        '''
        self.mutagenInterface = mutagen.File(self.audioFilepath)

        title = self._getTagValueFromMutagenInterface('title')
        artist = self._getTagValueFromMutagenInterface('artist')
        album = self._getTagValueFromMutagenInterface('album')
        albumArtist = self._getTagValueFromMutagenInterface('albumartist')
        composer = self._getTagValueFromMutagenInterface('composer')
        date = self._getTagValueFromMutagenInterface('date')
        genre = self._getTagValueFromMutagenInterface('genre')
        trackNumber = self._getTagValueFromMutagenInterface('tracknumber')
        totalTracks = self._getTagValueFromMutagenInterface('tracktotal')
        discNumber = self._getTagValueFromMutagenInterface('discnumber')
        totalDiscs = self._getTagValueFromMutagenInterface('disctotal')
        bpm = self._getTagValueFromMutagenInterface('bpm')
        key = self._getTagValueFromMutagenInterface('key')
        lyrics = self._getTagValueFromMutagenInterface('lyrics')
        comment = self._getTagValueFromMutagenInterface('comment')
        dateAdded = self._getTagValueFromMutagenInterface('date_added')
        dateAllPlays = self._getTagValueFromMutagenInterface('date_all_plays')
        dateLastPlayed = self._getTagValueFromMutagenInterface('date_last_played') 
        playCount = self._getTagValueFromMutagenInterface('play_count')
        votes = self._getTagValueFromMutagenInterface('votes')
        rating = self._getTagValueFromMutagenInterface('rating')
        otherTags = {}

        tagFieldKeysFlac = [
            'title', 
            'artist', 
            'album', 
            'albumartist', 
            'composer', 
            'date', 
            'genre', 
            'tracknumber', 
            'tracktotal', 
            'discnumber', 
            'disctotal', 
            'bpm', 
            'key', 
            'lyrics',  
            'comment', 
            'date_added', 
            'date_all_plays', 
            'date_last_played',
            'play_count',
            'votes', 
            'rating'
        ]

        mutagenTagKeys = self.mutagenInterface.tags.keys()
        relevantTagKeys = self._removeUnneededTagKeysFromTagKeysList(mutagenTagKeys)

        otherTagNames = []
        for tagKey in relevantTagKeys:
            if (tagKey.lower() not in tagFieldKeysFlac):
                otherTagNames.append(tagKey.lower())

        for tagNameKey in otherTagNames:
            tagValue = self._getTagValueFromMutagenInterface(tagNameKey)
            otherTags[tagNameKey] = tagValue

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

    def _removeUnneededTagKeysFromTagKeysList(self, flacKeys):
        keysToRemove = [
            'replaygain_album_gain',
            'replaygain_album_peak',
            'replaygain_track_gain',
            'replaygain_track_peak'
        ]

        for removeKey in keysToRemove:
            try:
                flacKeys.remove(removeKey)
            except:
                pass

        return flacKeys

    def _getTagValueFromMutagenInterface(self, mutagenKey):
        try:
            mutagenValue = self.mutagenInterface[mutagenKey]

            if (len(mutagenValue) == 1):
                tagValue = mutagenValue[0]
            elif (len(mutagenValue) > 1):
                tagValue = ';'.join(mutagenValue)
            else:
                tagValue = ''

        except KeyError:
            tagValue = ''

        return tagValue  

    def setTags(self, audioFileTags):
        '''
        '''
        self.mutagenInterface = mutagen.File(self.audioFilepath)

        self.mutagenInterface['date_all_plays'] = audioFileTags.dateAllPlays
        self.mutagenInterface['date_last_played'] = audioFileTags.dateLastPlayed
        self.mutagenInterface['play_count'] = audioFileTags.playCount
        self.mutagenInterface['votes'] = audioFileTags.votes
        self.mutagenInterface['rating'] = audioFileTags.rating

        self.mutagenInterface.save()