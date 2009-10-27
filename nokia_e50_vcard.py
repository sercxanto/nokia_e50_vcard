#!/usr/bin/python
#
#    nokia_e50_vcard.py
#
#    Converts vcard file for import into Nokia E50
#
#    Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import optparse
import os
import re
import shutil
import sys
import types

VERSIONSTRING = "0.1"


def makeUniqueName(text, names):
    '''Check if text is a VCard name ("N") entry and makes this name unique if
    already found in dict names. Background is that when multiple vcards with
    the same name entry are imported nokia phone only creates one entry and
    overwrites all fields with subsequent entry.
    For vcard 2.1 standard see http://www.imc.org/pdi/vcard-21.doc'''
    regex = re.compile("N:(?P<familyName>.*);(?P<givenName>.*);(?P<addNames>.*);(?P<namePref>.*);(?P<nameSuff>.*)")
    result = regex.search(text)
    # Check familyName and givenName because otherwise all entries without would be named "(0)" and so on
    if type(result) != types.NoneType and len(result.group("familyName")) > 0 and len(result.group("givenName")) > 0:
	simpleName = result.group("familyName") + ", " + result.group("givenName")
	if names.has_key(simpleName):
	    names[simpleName] = names[simpleName] + 1
	    # I sort my contacts on phone like "familyName, surname" so not unique names would
	    # show "familyName, surname (2)" and so on
	    resultText = "N:%s;%s (%d);%s;%s;%s\n" % (result.group("familyName"), result.group("givenName"), names[simpleName], result.group("addNames"), result.group("namePref"), result.group("nameSuff"))
	else:
	    names[simpleName] = 1
	    resultText = text
	return resultText
    else:
	return text


########### MAIN PROGRAM #############
def main():

    parser = optparse.OptionParser(
	    usage="%prog [options] vcardfile directory",
	    version="%prog " + VERSIONSTRING + os.linesep +
	    "Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de>",
	    epilog = "directory: Where to store the single vcard files. vcardfile: The vcardfile to split")
    
    parser.add_option("-d", "--debuglevel", dest="debuglevel",
	    type="int", default=logging.WARNING,
	    help="Sets numerical debug level, see library logging module. Default is 30 (WARNING). Possible values are CRITICAL 50, ERROR 40, WARNING 30, INFO 20, DEBUG 10, NOTSET 0. All log messages with debuglevel or above are printed. So to disable all output set debuglevel e.g. to 100.")

    (options, args) = parser.parse_args()

    logging.basicConfig(format="%(message)s", level=options.debuglevel)

    if len(args) < 2:
	parser.print_help()
	sys.exit(2)

    vcardFileName = os.path.expanduser(args[0])
    if not os.path.isfile(vcardFileName):
	logging.error("vcardFile not found")
	sys.exit(1)

    dirName = os.path.expanduser(args[1])
    if not os.path.isdir(dirName):
	logging.error("directory not found")
	sys.exit(1)
    
    try:
	vcardFile = open(vcardFileName, "r")
    except:
	logging.error("Cannot open vcard file")
	sys.exit(2)

    line = vcardFile.readline()
    splitVcardFileName = ""
    splitVcardFile = 0
    names = {} # track duplicate names
    i = -1
    while line != "":
	if line.find("BEGIN:VCARD") >= 0:
	    i = i + 1
	    splitVcardFileName = os.path.join(dirName,"%03d.vcf" % i)
	    splitVcardFile = open(splitVcardFileName, "w")
	    splitVcardFile.write(line)
	else:
	    if line.find("END:VCARD") >= 0:
		splitVcardFile.write(line)
		if type(splitVcardFile) == types.FileType and not file.closed:
		    file.close()
	    else:
                # Nokia seems to default to latin1
		line = unicode(line, "utf-8").encode("iso-8859-1")
		line = makeUniqueName(line, names)
		splitVcardFile.write(line)
	line = vcardFile.readline()

    vcardFile.close()




if __name__ == "__main__":
    main()

