# python

import lx, modo, replay, traceback, os, sys

kitpath = lx.eval('query platformservice alias ? "kit_mecco_replay:"')

# open event log
lx.eval('layout.createOrClose EventLog "Event Log_layout" true @macros.layouts@EventLog@ width:600 height:600 persistent:true')

# open replay palette
lx.eval('layout.createOrClose ReplayPalette ReplayPalette true "Replay Palette" width:400 height:600 persistent:true style:palette')

# -------------------
# BASIC FILE COMMANDS
# -------------------

# make sure we don't mess up any scene files
lx.eval('scene.closeAll')

test_file = 'Test01.LXM'

# Open a macro
try:
    lx.eval('replay.fileOpen {%s}' % os.path.join(kitpath, 'utest', test_file))
    lx.out("Opened %s" % test_file)
except:
    traceback.print_exc()

# Close a macro
try:
    lx.eval('replay.fileClose')
    lx.out("Closed %s" % test_file)
except:
    traceback.print_exc()

# Reopen macro
try:
    lx.eval('replay.fileOpen {%s}' % os.path.join(kitpath, 'utest', test_file))
    lx.out("Reopened %s" % test_file)
except:
    traceback.print_exc()

# New Macro
try:
    lx.eval('replay.fileNew')
    lx.out("Created new while %s was open." % test_file)
except:
    traceback.print_exc()

# Reopen macro
try:
    lx.eval('replay.fileOpen {%s}' % os.path.join(kitpath, 'utest', test_file))
    lx.out("Reopened %s" % test_file)
except:
    traceback.print_exc()

# Insert macro steps
try:
    lx.eval('replay.fileInsert {%s}' % os.path.join(kitpath, 'utest', test_file))
    lx.out("Inserted %s" % test_file)
except:
    traceback.print_exc()

# -----------------
# EXPORT TEST CASES
# -----------------

# Ask for a
file_path = modo.dialogs.dirBrowse('Where to save test files?')
# User cancelled. Abort.
if file_path is None:
    sys.exit()

# Save a macro
try:
    lx.eval('replay.fileSave {%s}' % os.path.join(file_path, 'fileSave.lxm'))
    lx.out("Saved %s" % 'fileSave.lxm')
except:
    traceback.print_exc()

# Export a macro as LXM
try:
    lx.eval('replay.fileExport lxm {%s}' % os.path.join(file_path, 'fileExport.lxm'))
    lx.out("Exported %s" % 'fileExport.lxm')
except:
    traceback.print_exc()

# Export a macro as Python
try:
    lx.eval('replay.fileExport py {%s}' % os.path.join(file_path, 'fileExport.py'))
    lx.out("Exported %s" % 'fileExport.py')
except:
    traceback.print_exc()

# Export a macro as JSON
try:
    lx.eval('replay.fileExport json {%s}' % os.path.join(file_path, 'fileExport.json'))
    lx.out("Exported %s" % 'fileExport.json')
except:
    traceback.print_exc()

# Close a macro
try:
    lx.eval('replay.fileClose')
    lx.out("Closed %s" % test_file)
except:
    traceback.print_exc()

# ----------------
# MACRO TEST CASES
# ----------------

test_files = ['Test01.LXM']

for test_file in test_files:

    # Open a macro
    try:
        lx.eval('replay.fileOpen {%s}' % os.path.join(kitpath, 'utest', test_file))
        lx.out("Opened %s" % test_file)
    except:
        traceback.print_exc()

    # Play a macro
    try:
        lx.eval('replay.play')
        lx.out("Played %s" % test_file)
    except:
        traceback.print_exc()

    lx.eval('!!scene.closeAll')

    # Step through an entire macro
    for n in range(len(replay.Macro().commands)):
        try:
            lx.eval('replay.step')
            lx.out("Ran %s step %s" % (test_file, n))
        except:
            lx.out("Failed %s step %s" % (test_file, n))
            traceback.print_exc()

    # Close a macro
    try:
        lx.eval('replay.fileClose')
        lx.out("Closed %s" % test_file)
    except:
        traceback.print_exc()
