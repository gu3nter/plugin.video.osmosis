# Copyright (C) 2016 stereodruid(J.G.) Mail: stereodruid@gmail.com
#
#
# This file is part of OSMOSIS
#
# OSMOSIS is free software: you can redistribute it. 
# You can modify it for private use only.
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.


# -*- coding: utf-8 -*-
import os
import time
import sys
from modules import create
from modules import guiTools
from modules import kodiDB
from modules import fileSys
from modules import moduleUtil

import utils
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import re

# Debug option pydevd:
if False:
    import pydevd
    pydevd.settrace(stdoutToServer=True, stderrToServer=True)

global thelist
thelist = None

ADDON_ID = 'plugin.video.osmosis'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
# PC Settings Info
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'MediaList.xml'))
Automatic_Update_Time = REAL_SETTINGS.getSetting('Automatic_Update_Time') 
represent = os.path.join(ADDON_PATH, 'icon.png')
itime = 900000000000000  # in miliseconds  

def readMediaList(purge=False):
    try:
        if xbmcvfs.exists(MediaList_LOC):
            fle = open(MediaList_LOC, "r")
            thelist = fle.readlines()
            fle.close()
            return thelist
    except:
        pass

def strm_update(selectedItems=None):
    try:
        if xbmcvfs.exists(MediaList_LOC):
            thelist = readMediaList() if selectedItems is None else selectedItems
            if len(thelist) > 0:
                dialogeBG = xbmcgui.DialogProgressBG()
                dialogeBG.create("OSMOSIS: " ,  'Total Update-Progress:')

                listLen = len(thelist)
                step = j = 100 / listLen
                for entry in thelist:
                    splits = entry.strip().split('|')
                    cType, name, url = splits[0], splits[1], splits[2]

                    try:
                        plugin_id = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), url)
                        if plugin_id:
                            module = moduleUtil.getModule(plugin_id.group(1))
                            if module and hasattr(module, 'update'):
                                url = module.update(name, url, 'video', thelist)
    
                        dialogeBG.update(j, "OSMOSIS total update process: " , "Current Item: " + name.replace('++RenamedTitle++','') + " Items left: " + str(listLen))
                        j += step
    
                        create.fillPluginItems(url, strm=True, strm_name=name, strm_type=cType)
                        listLen -= 1
                    except:
                        pass
                dialogeBG.close()
                xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (ADDON_NAME, "Next update in: " + Automatic_Update_Time + "h" , 5000, represent))
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". See your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[1]
        pass
