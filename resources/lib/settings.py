# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2016 Rob Webset
# SPDX-FileCopyrightText:  2020-2021 Peter J. Mello <admin@petermello.net>
#
# SPDX-License-Identifier: MPL-2.0

import os
import xbmc
import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon(id='service.addonsync')
ADDON_ID = ADDON.getAddonInfo('id')


# Common logging module
def log(txt, loglevel=xbmc.LOGDEBUG):
    if (ADDON.getSetting("logEnabled") == "true") or (loglevel != xbmc.LOGDEBUG):
        if isinstance(txt, str):
            txt = txt.decode("utf-8")
        message = u'%s: %s' % (ADDON_ID, txt)
        xbmc.log(msg=message.encode("utf-8"), level=loglevel)


# Checks if a directory exists (Do not use for files)
def dir_exists(dirpath):
    # There is an issue with password protected smb shares, in that they seem to
    # always return false for a directory exists call, so if we have a smb with
    # a password and user name, then we return true
    if '@' in dirpath:
        return True

    directoryPath = dirpath
    # The xbmcvfs exists interface require that directories end in a slash
    # It used to be OK not to have the slash in Gotham, but it is now required
    if (not directoryPath.endswith("/")) and (not directoryPath.endswith("\\")):
        dirSep = "/"
        if "\\" in directoryPath:
            dirSep = "\\"
        directoryPath = "%s%s" % (directoryPath, dirSep)
    return xbmcvfs.exists(directoryPath)


# There has been problems with calling join with non ascii characters,
# so we have this method to try and do the conversion for us
def os_path_join(dir, file):
    # Check if it ends in a slash
    if dir.endswith("/") or dir.endswith("\\"):
        # Remove the slash character
        dir = dir[:-1]

    # Convert each argument - if an error, then it will use the default value
    # that was passed in
    try:
        dir = dir.decode("utf-8")
    except:
        pass
    try:
        file = file.decode("utf-8")
    except:
        pass
    return os.path.join(dir, file)


# Performs a nested copy of one directory to another
def nestedCopy(rootSourceDir, rootTargetDir):
    log("nestedCopy: Copy %s to %s" % (rootSourceDir, rootTargetDir))

    # Make sure the target directory exists
    xbmcvfs.mkdirs(rootTargetDir)

    dirs, files = xbmcvfs.listdir(rootSourceDir)

    for file in files:
        try:
            file = file.decode("utf-8")
        except:
            pass
        sourceFile = "%s%s" % (rootSourceDir, file)
        targetFile = "%s%s" % (rootTargetDir, file)
        log("nestedCopy: Copy file %s to %s" % (sourceFile, targetFile))
        xbmcvfs.copy(sourceFile, targetFile)

    for adir in dirs:
        try:
            adir = adir.decode("utf-8")
        except:
            pass
        sourceDir = "%s%s/" % (rootSourceDir, adir)
        targetDir = "%s%s/" % (rootTargetDir, adir)
        log("nestedCopy: Copy directory %s to %s" % (sourceDir, targetDir))
        nestedCopy(sourceDir, targetDir)


def nestedDelete(rootDir):
    # If the file already exists, delete it
    if dir_exists(rootDir):
        # Remove the png files in the directory first
        dirs, files = xbmcvfs.listdir(rootDir)
        # Remove nested directories first
        for adir in dirs:
            nestedDelete(os_path_join(rootDir, adir))
        # If there are any nested files remove them
        for aFile in files:
            xbmcvfs.delete(os_path_join(rootDir, aFile))
        # Now remove the actual directory
        xbmcvfs.rmdir(rootDir)
    else:
        log("nestedDelete: Directory %s does not exist" % rootDir)


##############################
# Stores Various Settings
##############################
class Settings():
    FILTER_ALL = 0
    FILTER_INCLUDE = 1
    FILTER_EXCLUDE = 2

    @staticmethod
    def isFirstUse():
        return ADDON.getSetting("isFirstUse") == 'true'

    @staticmethod
    def setFirstUse(useValue='false'):
        ADDON.setSetting("isFirstUse", useValue)

    @staticmethod
    def getCentralStoreLocation():
        centralStoreLocation = ADDON.getSetting("centralStoreLocation")
        # Make sure the location ends with a slash
        if ('/' in centralStoreLocation) and (not centralStoreLocation.endswith('/')):
            centralStoreLocation = "%s/" % centralStoreLocation
        elif ('\\' in centralStoreLocation) and (not centralStoreLocation.endswith('\\')):
            centralStoreLocation = "%s\\" % centralStoreLocation
        return centralStoreLocation

    @staticmethod
    def isMasterInstallation():
        # Safer to check for slave type, as master will not overwrite
        if int(ADDON.getSetting("installationType")) == 1:
            return False
        return True

    @staticmethod
    def isRunOnStartup():
        return ADDON.getSetting('runOnStartup') == 'true'

    @staticmethod
    def getCheckInterval():
        # If we do not want to run on startup, then the interval is
        # just the once
        if not Settings.isRunOnStartup():
            return 0
        return int(float(ADDON.getSetting('checkInterval')))

    @staticmethod
    def isRestartUpdatedServiceAddons():
        return ADDON.getSetting('restartUpdatedServiceAddons') == 'true'

    @staticmethod
    def isForceVersionMatch():
        return ADDON.getSetting('forceVersionMatch') == 'true'

    @staticmethod
    def getFilterType():
        index = int(ADDON.getSetting("filterType"))
        filterType = Settings.FILTER_ALL
        if index == 1:
            filterType = Settings.FILTER_INCLUDE
        elif index == 2:
            filterType = Settings.FILTER_EXCLUDE

        return filterType

    @staticmethod
    def getExcludedAddons():
        return ADDON.getSetting('excludedAddons')

    @staticmethod
    def getIncludedAddons():
        return ADDON.getSetting('includedAddons')

    @staticmethod
    def setExcludedAddons(value=""):
        ADDON.setSetting('excludedAddons', value)

    @staticmethod
    def setIncludedAddons(value=""):
        ADDON.setSetting('includedAddons', value)
