# python

import lx, modo, replay, traceback, os

kitpath = lx.eval('query platformservice alias ? "kit_mecco_replay:"')

# open event log
lx.eval('layout.createOrClose EventLog "Event Log_layout" true @macros.layouts@EventLog@ width:600 height:600 persistent:true')

# -------------------
# BASIC FILE COMMANDS
# -------------------

# make sure we don't mess up any scene files
lx.eval('scene.closeAll')

test_file = ['Test01.LXM']

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

# Close a macro
try:
    lx.eval('replay.fileClose')
    lx.out("Closed %s" % test_file)
except:
    traceback.print_exc()

# --------------
# RECORD A MACRO
# --------------

try:
    lx.eval('replay.record true')
    lx.out("Started recording.")

    lx.eval('script.run hash:macro.scriptservice:19601433555:macro')
    lx.eval('transform.channel name:pos.Y value:2.0')
    lx.eval('script.run hash:macro.scriptservice:27554333777:macro')
    lx.eval('transform.channel name:pos.Y value:-2.0')
    lx.eval('script.run hash:macro.scriptservice:32235733333:macro')
    lx.eval('script.run hash:macro.scriptservice:47158833888:macro')
    lx.eval('transform.channel name:pos.X value:2.0')
    lx.eval('script.run hash:macro.scriptservice:45422344000:macro')
    lx.eval('transform.channel name:pos.X value:-2.0')
    lx.eval('transform.channel name:rot.X value:90.0')
    lx.eval('select.itemType type:mesh')
    lx.eval('layer.mergeMeshes comp:True')
    lx.eval('transform.channel name:rot.Z value:180.0')
    lx.eval('poly.setMaterial name:GreenTestMaterial color:"0.0443 0.5543 0.1335" diffuse:0.8 specular:0.04 smoothing:True default:False useLib:False')
    lx.out("Ran some commands for testing.")

    lx.eval('replay.record false')
    lx.out("Stopped recording.")
except:
    traceback.print_exc()

# -----------------
# EXPORT TEST CASES
# -----------------

# Ask for a
file_path = modo.dialogs.dirBrowse(title)
# User cancelled. Abort.
if file_path is None:
    return

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
