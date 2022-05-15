'''
Tests for mlu.tags.io, which also tests the mlu.tags.audiofmt modules.

'''

import unittest
import sys
import os
from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

# Add project root to PYTHONPATH so MLU modules can be imported
scriptPath = os.path.dirname(os.path.realpath(__file__))
projectRoot = os.path.abspath(os.path.join(scriptPath ,"../.."))
sys.path.insert(0, projectRoot)

from mlu.settings import MLUSettings
import mlu.tags.io
import mlu.tags.values
import mlu.tags.audiofmt.flac
import mlu.tags.audiofmt.mp3
import mlu.tags.audiofmt.m4a
import test.helpers.common

class TestAudioFile:
    '''
    Class representing a test audio file and the 'actual' tag values that it has. This is a data
    structure used by the TestData class.
    '''
    def __init__(self, filepath, tagValues):
        self.filepath = filepath
        self.tagValues = tagValues

class TestData:
    '''
    Class representing the test data that will be used for a single test run of the tags.io module.
    This data consists of the test audio filepaths and the 'actual' tag values for each of these
    files.

    These audio files are predefined, static files which have had their tags set through some 
    external methods (not set using MLU), and the tags.json file defines these tags for the files.
    '''
    def __init__(self, testAudioFilesDir, testAudioTagsFile):

        testAudioFilesTagData = mypycommons.file.readJsonFile(testAudioTagsFile)

        flacTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'flac'][0]
        mp3TestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'mp3'][0]
        m4aTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'm4a'][0]

        self.testAudioFilesFLAC = []
        self.testAudioFilesMp3 = []
        self.testAudioFilesM4A = []

        for flacTestFile in flacTestFilesData:
            testAudioFile = TestAudioFile(
                filepath=mypycommons.file.joinPaths(testAudioFilesDir, flacTestFile['filename']),
                tagValues=flacTestFile['tagValues']
            )
            self.testAudioFilesFLAC.append(testAudioFile)

        for mp3TestFile in mp3TestFilesData:
            testAudioFile = TestAudioFile(
                filepath=mypycommons.file.joinPaths(testAudioFilesDir, mp3TestFile['filename']),
                tagValues=mp3TestFile['tagValues']
            )
            self.testAudioFilesMp3.append(testAudioFile)

        for m4aTestFile in m4aTestFilesData:
            testAudioFile = TestAudioFile(
                filepath=mypycommons.file.joinPaths(testAudioFilesDir, m4aTestFile['filename']),
                tagValues=m4aTestFile['tagValues']
            )
            self.testAudioFilesM4A.append(testAudioFile)


        self.notSupportedAudioFile = "{}.ogg".format(test.helpers.common.getRandomFilepath())
        self.notExistFile = test.helpers.common.getRandomFilepath()



class TestTagsIOModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        '''
        Sets up the test data for the tests of the tags.io module. The test audio files are copied
        from the test resource dir to the mlu cache dir, where they will be manipulated by the tests
        while preserving the original test data files.
        '''
        super(TestTagsIOModule, self).setUpClass

        testAudioFilesDir = mypycommons.file.joinPaths(MLUSettings.testDataDir, 'test-audio-files')
        testAudioTagsFile = mypycommons.file.joinPaths(MLUSettings.testDataDir, 'test-audio-files-tags.json')
        tempTestAudioFilesDir = mypycommons.file.joinPaths(MLUSettings.tempDir, 'test-audio-files')

        mypycommons.file.createDirectory(tempTestAudioFilesDir)

        # copy the test audio files from the static test files dir to the temp cache test files dir
        # also copy the tags.json file
        testAudioFilesSrc = mypycommons.file.getChildPathsRecursive(rootDirPath=testAudioFilesDir, pathType='file')
        for testAudioFile in testAudioFilesSrc:
            mypycommons.file.copyToDirectory(path=testAudioFile, destDir=tempTestAudioFilesDir)

        self.testData = TestData(tempTestAudioFilesDir, testAudioTagsFile)


    @classmethod
    def tearDownClass(self):  
        super(TestTagsIOModule, self).tearDownClass      
        mypycommons.file.deletePath(MLUSettings.tempDir)

    def test_AudioFileMetadataHandler_Constructor(self):
        '''
        Tests the constructor of the AudioFileTagIOHandler class to ensure only supported audio
        formats are accepted and that only existing files are accepted.
        '''
        # Test nonexisting file given
        self.assertRaises(ValueError, mlu.tags.io.AudioFileMetadataHandler, self.testData.notExistFile)

        # Test FLAC file given
        handler = mlu.tags.io.AudioFileMetadataHandler(self.testData.testAudioFilesFLAC[0].filepath)
        self.assertEqual(handler._audioFileType, 'flac')
        self.assertTrue(isinstance(handler._audioFmtHandler, mlu.tags.audiofmt.flac.AudioFormatHandlerFLAC))

        # Test MP3 file given
        handler = mlu.tags.io.AudioFileMetadataHandler(self.testData.testAudioFilesMp3[0].filepath)
        self.assertEqual(handler._audioFileType, 'mp3')
        self.assertTrue(isinstance(handler._audioFmtHandler, mlu.tags.audiofmt.mp3.AudioFormatHandlerMP3))


        # Test M4A file given
        handler = mlu.tags.io.AudioFileMetadataHandler(self.testData.testAudioFilesM4A[0].filepath)
        self.assertEqual(handler._audioFileType, 'm4a')
        self.assertTrue(isinstance(handler._audioFmtHandler, mlu.tags.audiofmt.m4a.AudioFormatHandlerM4A))

        # Test non-supported filetype given
        self.assertRaises(Exception, mlu.tags.io.AudioFileMetadataHandler, self.testData.notSupportedAudioFile)

    def test_AudioFileMetadataHandler_FLAC(self):
        '''
        Tests tag reading/writing for a test FLAC file.
        '''
        for testAudioFile in self.testData.testAudioFilesFLAC:
            handler = mlu.tags.io.AudioFileMetadataHandler(testAudioFile.filepath)
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)
            
    def test_AudioFileMetadataHandler_MP3(self):
        '''
        Tests tag reading/writing for a test Mp3 file.
        '''
        for testAudioFile in self.testData.testAudioFilesMp3:
            handler = mlu.tags.io.AudioFileMetadataHandler(testAudioFile.filepath)
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)

    def test_AudioFileMetadataHandler_M4A(self):
        '''
        Tests tag reading/writing for a test M4A file.
        '''
        for testAudioFile in self.testData.testAudioFilesM4A:
            handler = mlu.tags.io.AudioFileMetadataHandler(testAudioFile.filepath)
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)

    def _checkAudioFileTagIOHandlerRead(self, audioFileMetadataHandler, expectedTagValues):
        '''
        Tests tag reading for any given test AudioFileTagIOHandler instance. Used as a 
        helper function.

        The test will check that the given expected tag values match those that are read using the
        handler.

        Params:
            audioFileTagIOHandler: the handler instance to test (is defined with a test audio file type)
            expectedTagValues: dict of the expected tag names and values that this handler should 
                be expected to read out
        '''
        tags = audioFileMetadataHandler.getTags()
        actualTagValues = tags.__dict__        

        # Remove the otherTags value from expected tags (we will check this later)
        try:
            expectedOtherTags = expectedTagValues['OTHER_TAGS']
            del expectedTagValues['OTHER_TAGS']
        except KeyError:
            expectedOtherTags = {}

        # Check that all the expected tags are in the returned tags
        for tagName in expectedTagValues:
            self.assertIn(tagName, actualTagValues)

        # Check that the expected and actual tags values match
        for tagName in expectedTagValues:
            expectedTagValue = expectedTagValues[tagName]
            actualTagValue = actualTagValues[tagName]
            self.assertEqual(expectedTagValue, actualTagValue)

        # Check the other tags values
        for expectedOtherTag in expectedOtherTags:
            expectedTagName = expectedOtherTag['name']
            expectedTagValue = expectedOtherTag['value']

            # test that the other_tags contains each other tag name
            self.assertIn(expectedTagName, actualTagValues['OTHER_TAGS'])

            self.assertEqual(expectedTagValue, actualTagValues['OTHER_TAGS'][expectedTagName])


    def _checkAudioFileTagIOHandlerWrite(self, audioFileTagIOHandler):
        '''
        Tests tag writing for any given test AudioFileTagIOHandler instance. Used as a 
        helper function.

        The test will check that new tag values can be written via the handler.

        Params:
            audioFileTagIOHandler: the handler instance to test (is defined with a test audio file type)
        '''
        tags = audioFileTagIOHandler.getTags()
        newTagValues = {}

        newTagValues['dateAllPlays'] = test.helpers.common.getRandomString(length=20, allowSpecial=False)
        newTagValues['dateLastPlayed'] = test.helpers.common.getRandomString(length=20, allowSpecial=False)
        newTagValues['playCount'] = test.helpers.common.getRandomString(length=20, allowSpecial=False)
        newTagValues['votes'] = test.helpers.common.getRandomString(length=20, allowSpecial=False)
        newTagValues['rating']  = test.helpers.common.getRandomString(length=20, allowSpecial=False)

        tags.dateAllPlays = newTagValues['dateAllPlays']
        tags.dateLastPlayed = newTagValues['dateLastPlayed']
        tags.playCount = newTagValues['playCount']
        tags.votes = newTagValues['votes']
        tags.rating = newTagValues['rating']

        audioFileTagIOHandler.setTags(tags)

        # Use the read test function to ensure the tags are now set to the new tag values 
        self._checkAudioFileTagIOHandlerRead(audioFileTagIOHandler, expectedTagValues=newTagValues)

if __name__ == '__main__':
    unittest.main()