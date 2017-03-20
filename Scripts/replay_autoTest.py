# python

import lx, modo, replay, traceback, os, sys, filecmp

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

# ----------------
# MACRO TEST CASES
# ----------------

test_files = [
    'allvisible.LXM',
    'Blank_Macro_001.LXM',
    'fixsymm_origin_x.LXM',
    'fixsymm_origin_y.LXM',
    'fixsymm_origin_z.LXM',
    'pp_poly_collapse.py',
    'pp_spinedge_right.py',
    'selected_faces_to_new_mesh_item.lxm',
    'subdiv_to_poly.lxm',
    'tear_polygons.lxm',
    'Test01.LXM',
    'Test02.LXM',
    'toggle_wire.lxm',
    'toolBlock.lxm',
    'triangulate_radial.lxm',
    'working_Macro_001.LXM'
    ]

for test_file in test_files:

    name = os.path.splitext(test_file)[0]

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

    # Save a macro
    try:
        lx.eval('replay.fileSave {%s}' % os.path.join(file_path, name + '_save.lxm'))
        lx.out("Saved %s" % name + '_save.lxm')
    except:
        lx.out("Save failed: %s" % name + '_save.lxm')
        traceback.print_exc()

    for export_format in ['lxm', 'py', 'json']:
        filename = name + '_export.' + export_format

        # Export macro
        try:
            lx.eval('replay.fileExport %s {%s}' % (export_format, os.path.join(file_path, filename)))
            lx.out("Exported %s" % filename)
        except:
            lx.out("Export failed: %s" % filename)
            traceback.print_exc()

    for export_format in ['lxm', 'py', 'json']:
        filename = name + '_export.' + export_format
        test_file_fullpath = os.path.join(file_path, filename)
        comparison_filename = name + "_" + export_format + ".lxm"
        comparison_file_fullpath = os.path.join(file_path, comparison_filename)

        # Reopen exported macro
        try:
            lx.eval('replay.fileOpen {%s}' % test_file_fullpath)
            lx.out("Opened %s" % filename)
        except:
            lx.out("Failed to re-open %s" % filename)
            traceback.print_exc()

        # Re-Export macro for comparison with original
        try:
            lx.eval('replay.fileExport lxm {%s}' % comparison_file_fullpath)
            lx.out("Exported %s" % comparison_filename)
        except:
            lx.out("Export failed: %s" % comparison_filename)
            traceback.print_exc()

        # Compare re-exported file with original
        try:
            if filecmp.cmp(test_file_fullpath, comparison_file_fullpath):
                lx.out("%s and %s match. Pass." % (filename, comparison_filename))
            else:
                lx.out("%s and %s do not match. FAIL." % (filename, comparison_filename))
        except:
            lx.out("Failed to compare %s with %s" % (filename, comparison_filename))
            traceback.print_exc()

    # Close a macro
    try:
        lx.eval('replay.fileClose')
        lx.out("Closed %s" % test_file)
    except:
        traceback.print_exc()
