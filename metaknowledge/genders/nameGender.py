#Written by Reid McIlroy-Young for Dr. John McLevey, University of Waterloo 2016
import zipfile
import io
import csv
import os.path
import urllib

from ..mkExceptions import GenderException

dataURL = 'https://github.com/networks-lab/globalnamedata/archive/0.3.zip'
americanNamesPath = 'globalnamedata-0.3/assets/usprocessed.csv'
ukNamesPath = 'globalnamedata-0.3/assets/ukprocessed.csv'

targetFilePath = os.path.join(os.path.normpath(os.path.dirname(__file__)), 'namesData.csv')

csvFields = [
    'Name',
    'years.appearing',
    'count.male',
    'count.female',
    'prob.gender',
    'obs.male',
    'est.male',
    'upper',
    'lower'
]

#global to reduce need to reload dict
mappingDict = None

def downloadData(useUK = False):
    zipFile = io.BytesIO(urllib.request.urlopen(dataURL).read())
    if useUK:
        namesFile = zipfile.ZipFile(zipFile).open(ukNamesPath)
    else:
        namesFile = zipfile.ZipFile(zipFile).open(americanNamesPath)
    with open(targetFilePath, 'wb') as f:
        f.write(namesFile.read())

def getMapping(useUK = False):
    if not os.path.isfile(targetFilePath):
        downloadData(useUK)
    retDict = {}
    with open(targetFilePath) as f:
        reader = csv.DictReader(f, fieldnames = csvFields)
        next(reader)
        for line in reader:
            retDict[line['Name'].title()] = line['prob.gender']
    return retDict

def nameStringGender(s, noExcept = False):
    """Expects `first, last`"""
    global mappingDict
    try:
        first = s.split(', ')[1].split(' ')[0].title()
    except IndexError:
        if noExcept:
            return 'Unknown'
        else:
            return GenderException("The given String: '{}' does not have a  last name, first name pair in with a ', ' seperation.".format(s))
    if mappingDict is None:
        mappingDict = getMapping()
    return mappingDict.get(first, 'Unknown')

def recordGenders(R):
    return {auth : nameStringGender(auth, noExcept = True) for auth in R.get('authorsFull', [])}
