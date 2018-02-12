#
# Load the libraries that are used in these commands.
#
from fman import DirectoryPaneCommand, show_alert,  show_prompt, clear_status_message, PLATFORM, YES, NO, DATA_DIRECTORY, FMAN_VERSION
from fman.url import as_human_readable, splitscheme
from fman.fs import move_to_trash
import subprocess
import re

#
# Function:    NewMoveToTrash
#
# Description:  This command moves files and directories to the trash if Finder is
#                       running. Otherwise, it deletes them using a low level delete.
#


class NewMoveToTrash(DirectoryPaneCommand):

    aliases = ('Delete', 'Move to trash', 'Move to recycle bin')

    def __call__(self):
        fmanv = 0
        if isinstance(FMAN_VERSION, str):
            fmanvParts = FMAN_VERSION.split('.')
            if fmanvParts[0] == '0':
                fmanv = int(fmanvParts[1])
        else:
            fmanv = FMAN_VERSION
        to_delete = self.get_chosen_files()
        if not to_delete:
            show_alert('No file is selected!')
            return
        if len(to_delete) > 1:
            description = 'these %d items' % len(to_delete)
        else:
            description = as_human_readable(to_delete[0])
        trash = 'Recycle Bin' if PLATFORM == 'Windows' else 'Trash'
        choice = show_alert(
            "Do you really want to move %s to the %s?" % (description, trash), YES | NO, YES
        )
        if choice & YES:
            file_system, file_path = splitscheme(to_delete[0])
            if (PLATFORM != 'Mac') or (file_system != 'file://'):
                move_to_trash(*to_delete)
            else:
                pluginLoc = DATA_DIRECTORY + "/Plugins/FlexibleTrash/"
                if fmanv > 4:
                    pluginLoc = DATA_DIRECTORY + "/Plugins/Third-party/FlexibleTrash/"
                finderFound = subprocess.run([pluginLoc + "finderRunning"], stdout=subprocess.PIPE)
                if re.search('not running',finderFound.stdout.decode("utf-8")) == None:
                    for item in to_delete:
                        subprocess.run([pluginLoc + "trash", as_human_readable(item)])
                else:
                    for item in to_delete:
                        subprocess.run(["rm", "-Rf", as_human_readable(item)])
