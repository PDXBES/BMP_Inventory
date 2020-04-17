#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      DASHNEY
#
# Created:     04/02/2015
# Copyright:   (c) DASHNEY 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
from utilities import reorder_fields, rename_fields, addMessage
from BMP_tools import add_StandardFields, incrementField, fillField, fillField_fromAnother

arcpy.env.overwriteOutput = True

temp = r"C:\temp\BMP_working.gdb"
if not arcpy.Exists(temp):
    arcpy.CreateFileGDB_management(r"C:\temp", "BMP_working.gdb")

#sde connection to egh_public
egh_public = r"\\oberon\grp117\DAshney\Scripts\connections\egh_public on gisdb1.rose.portland.local.sde"

#input feature classes
addMessage("Getting inputs")
collection_nodes = egh_public + r"\EGH_PUBLIC.ARCMAP_ADMIN.collection_points_bes_pdx"
collection_links = egh_public + r"\EGH_PUBLIC.ARCMAP_ADMIN.collection_lines_bes_pdx"
inflow_controls = egh_public + r"\EGH_PUBLIC.ARCMAP_ADMIN.ic_streettargets_bes_pdx"
ecoroof_pnts = egh_public + r"\EGH_PUBLIC.ARCMAP_ADMIN.ecoroof_pts_bes_pdx"
  #private facilities are a snapshot provided by Loren Shelley - ask for a refresh as needed
private = r"\\oberon\modeling\GridMaster\BMP\PRF\ARC\Working\2018_setup\data\MIP_Private_SMFs_Jan2015.mdb\MIP_Facilities_Jan2015"

final_output = r"\\oberon\modeling\GridMaster\BMP\PRF\ARC\Working\2018_setup\data\BMP_update_2018.gdb"

links_sub = "links_sub"
arcpy.MakeFeatureLayer_management(collection_links, links_sub, "UNITTYPE in ('CHDTC', 'CHRTF', 'CHSWL', 'STINF','CHGRSTFA') AND SERVSTAT = 'IN'")

arcpy.FeatureVerticesToPoints_management(links_sub,temp + r"\vertex_to_point","END")

print "done"


