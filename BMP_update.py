#-------------------------------------------------------------------------------
# Name:        BMP_update
# Purpose:
#
# Author:      DCA - BES - ASM
#
# Created:     30/01/2015
#
#
#-------------------------------------------------------------------------------
import arcpy
from utilities import reorder_fields, rename_fields, addMessage
from tools import add_StandardFields, incrementField, fillField, fillField_fromAnother,fillField_ifOverlap, fillField_Conditional,calcField_fromOverlap,fillField_fromDict,calcField_withinDistance

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
ecoroof_pnts = egh_public + r"\EGH_PUBLIC.ARCMAP_ADMIN.ecoroof_pts_bes_pdx"
streams = egh_public + r"\EGH_PUBLIC.ARCMAP_ADMIN.stream_lines_pdx"
private = egh_public + "r\EGH_PUBLIC.ARCMAP_ADMIN.priv_mip_strm_facs_bes_pdx"
westside = r"\\oberon\modeling\GridMaster\BMP\PRF\ARC\Working\2018_setup\data\update_input.mdb\westside_city"
ms4 = egh_public + r"\EGH_PUBLIC.ARCMAP_ADMIN.of_drainage_bounds_bes_pdx"
# part of these are Kevin's revised subwatersheds - does not include Springbrook Creek
subwatersheds = egh_public + r"\EGH_PUBLIC.ARCMAP_ADMIN.ms4_catchments_bes_pdx"

final_output = r"\\oberon\modeling\GridMaster\BMP\PRF\ARC\Working\2018_setup\data\BMP_update_2018.gdb"

#snapshot and subset data based on established unit types - these must be re-established with each MS4 submittal"
addMessage("Creating data subsets")
links_sub = "links_sub"
nodes_sub = "nodes_sub"
#no need to subset ecoroofs
private_sub = "private_sub"
ms4_sub = "ms4_sub"
subwatersheds_sub = "subwatesheds_sub"

#create in memory versions of subsets - check this every run - prob want to pull these out into thier own lists to reference
arcpy.MakeFeatureLayer_management(collection_links, links_sub, "UNITTYPE in ('CHDTC', 'CHRTF', 'CHSWL', 'STINF','CHGRSTFA') AND SERVSTAT = 'IN'")
arcpy.MakeFeatureLayer_management(collection_nodes, nodes_sub, "(UNITTYPE in ('DVT', 'MSTF', 'PND', 'SBX', 'SED', 'SF', 'SST') or SUBTYPE in ('Filterra', 'STMFLTR', 'CNSTRTWLND', 'DRYINFPOND', 'SPILLPOND' , 'WETPOND')) AND SERVSTAT = 'IN'")
arcpy.MakeFeatureLayer_management(private, private_sub, "[FirstOfCode] in (' Constructed Treatment Wetland', 'Contained Planter Box', 'Detention Pond - Dry',+\
 'Detention Pond - Wet', 'Drywell', 'Ecoroof', 'Flow Through Planter Box', 'Infiltration Basin', 'Infiltration Planter Box', 'Infiltration Trench',+\
  'Porous Pavement', 'Sand Filter', 'Sedimentation Manhole', 'Silt Basin', 'Soakage Trench', 'Swale', 'Vegetated Filter')")
arcpy.MakeFeatureLayer_management(ms4, ms4_sub, "Basin <>'N/A' and Basin is not Null AND Boundary_Type= 'MS4'")
arcpy.MakeFeatureLayer_management(subwatersheds, subwatersheds_sub, "Basin <>'N/A'")

#copy subsets to output
addMessage("Copying subset results")
arcpy.CopyFeatures_management(nodes_sub, temp + r"\DME_nodes", "", "0", "0", "0")
arcpy.CopyFeatures_management(private_sub, temp + r"\private", "", "0", "0", "0")
arcpy.CopyFeatures_management(ecoroof_pnts, temp + r"\ecoroofs", "", "0", "0", "0")

#convert DME links to downstream node locations (preserve link attribution)
addMessage("Converting DME links to points")
arcpy.FeatureVerticesToPoints_management(links_sub,temp + r"\LinkstoPoint","END")

#add required fields to layers
add_StandardFields(temp + r"\LinkstoPoint")
add_StandardFields(temp + r"\DME_nodes")
add_StandardFields(temp + r"\private")
add_StandardFields(temp + r"\ecoroofs")

#populate required fields

#populate UID fields
incrementField(temp + r"\LinkstoPoint")
incrementField(temp + r"\DME_nodes")
incrementField(temp + r"\private")
incrementField(temp + r"\ecoroofs")

#populate Data_Source fields
fillField(temp + r"\LinkstoPoint","Data_Source","collection_lines")
fillField(temp + r"\DME_nodes","Data_Source","collection_nodes")
fillField(temp + r"\private","Data_Source","private")
fillField(temp + r"\ecoroofs","Data_Source","ecoroofs")

#populate Original ID fields
fillField_fromAnother(temp + r"\LinkstoPoint","Original_ID","GLOBALID")
fillField_fromAnother(temp + r"\DME_nodes","Original_ID","GLOBALID")
fillField_fromAnother(temp + r"\private","Original_ID","FAC_ID")
fillField_fromAnother(temp + r"\ecoroofs","Original_ID","PROPERTYID")

#populate Original Type fields
fillField_fromAnother(temp + r"\LinkstoPoint","Original_Type","UNITTYPE")
fillField_fromAnother(temp + r"\DME_nodes","Original_Type","UNITTYPE")
fillField_fromAnother(temp + r"\private","Original_Type","FirstOfCode")
fillField(temp + r"\ecoroofs","Original_Type","Ecoroof")

#populate Gen Type fields
fillField_fromAnother(temp + r"\LinkstoPoint","Gen_Type","DETAIL_SYMBOL")
fillField_fromAnother(temp + r"\DME_nodes","Gen_Type","DETAIL_SYMBOL")

fillField_fromAnother(temp + r"\private","Gen_Type","FirstOfCode")
fillField(temp + r"\ecoroofs","Gen_Type","Ecoroof")

#populate Install Date fields - verify availability for private
fillField_fromAnother(temp + r"\LinkstoPoint","InstallDate","INSTALL_DATE")
fillField_fromAnother(temp + r"\DME_nodes","InstallDate","INSTALL_DATE")
fillField_fromAnother(temp + r"\private","InstallDate","FirstOfOnMSigDate")
fillField_fromAnother(temp + r"\ecoroofs","InstallDate","YEAR_")


#populate As Built fields - available for collection links and nodes
fillField_fromAnother(temp + r"\LinkstoPoint","As_Built","JOBNO")
fillField_fromAnother(temp + r"\DME_nodes","As_Built","JOBNO")

#populate Subwatershed field with values
calcField_fromOverlap(temp + r"\LinkstoPoint",subwatersheds_sub,"Subwatershed","Basin")
calcField_fromOverlap(temp + r"\DME_nodes",subwatersheds_sub,"Subwatershed","Basin")
calcField_fromOverlap(temp + r"\private",subwatersheds_sub,"Subwatershed","Basin")
calcField_fromOverlap(temp + r"\ecoroofs",subwatersheds_sub,"Subwatershed","Basin")

#populate MS4 field with 1, else with 0
fillField_ifOverlap(temp + r"\LinkstoPoint",ms4_sub,"MS4",1)
fillField_ifOverlap(temp + r"\DME_nodes",ms4_sub,"MS4",1)
fillField_ifOverlap(temp + r"\private",ms4_sub,"MS4",1)
fillField_ifOverlap(temp + r"\ecoroofs",ms4_sub,"MS4",1)

#   populate those not within MS4 with 0
fillField_Conditional(temp + r"\LinkstoPoint","MS4",0)
fillField_Conditional(temp + r"\DME_nodes","MS4",0)
fillField_Conditional(temp + r"\private","MS4",0)
fillField_Conditional(temp + r"\ecoroofs","MS4",0)


#populate ACWA values
# if UNITTYPES (above) change then the assignments will need to change as well

#1st row = DME nodes
assignments = ({'CNFLTR':2,'DVT':7,'PND':4,'SBX':7,'SED':7,'SF':2,'SST':7,
#2nd row = DME links
'CHDTC':5,'CHPLNT':2,'CHRTF':5,'CHSWL':5,'STINF':10,'CHGRSTFA':5,
#3rd row = inflow controls
'c':10,'C':10,'p':9,
#4th - 8th row = private (MIP)
'Constructed Treatment Wetland':6,'Contained Planter Box':2,'Detention Pond - Dry':3,
'Detention Pond - Wet':4,'Drywell':10,'Ecoroof':8,'Flow Through Planter Box':2,
'Infiltration Basin':10,'Infiltration Planter Box':10,'Infiltration Trench':10,
'Porous Pavement':9,'Sand Filter':2,'Sedimentation Manhole':7,'Silt Basin':2,
'Soakage Trench':10,'Swale':5,'Vegetated Filter':5,
#9th row = ecoroofs
'Ecoroof':8})

ACWA = ({1:"Centrifugal Seperator Hydrodynamic Device",
2:"Filters (Leaf/Sand/Other)",
3:"Ponds, Dry Vegetated Detention Pond",
4:"Ponds - Wet Retention Basin",
5:"Swales - Vegetated Filter Strips",
6:"Wetlands - Constructed Surface Flow",
7:"Sediment Manhole",
8:"Green Roofs (4in substrate)",
9:"Porous Pavement",
10:"Infiltration Facility",
11:"Vegetated Ditch"})

fillField_fromDict(temp + r"\LinkstoPoint",assignments,"Original_Type","ACWA_ID")
fillField_fromDict(temp + r"\DME_nodes",assignments,"Original_Type","ACWA_ID")
fillField_fromDict(temp + r"\private",assignments,"Original_Type","ACWA_ID")
fillField_fromDict(temp + r"\ecoroofs",assignments,"Original_Type","ACWA_ID")

fillField_fromDict(temp + r"\LinkstoPoint",ACWA,"ACWA_ID","ACWA_Type")
fillField_fromDict(temp + r"\DME_nodes",ACWA,"ACWA_ID","ACWA_Type")
fillField_fromDict(temp + r"\private",ACWA,"ACWA_ID","ACWA_Type")
fillField_fromDict(temp + r"\ecoroofs",ACWA,"ACWA_ID","ACWA_Type")

#separate process for ACWA type 11 (ditches on westside of river)
links_ACWA = arcpy.MakeFeatureLayer_management(temp + r"\LinkstoPoint", "links_ACWA", "UNITTYPE in ('CHDTC')")
fillField_ifOverlap(links_ACWA,westside,"ACWA_ID",11)
fillField_fromDict(links_ACWA,ACWA,"ACWA_ID","ACWA_Type")

#re-order fields and drop those not needed
addMessage("Re ordering fields")

reorder = ['UID','Original_ID','As_Built','InstallDate','MS4','Data_Source','Original_Type','Gen_Type','ACWA_ID','ACWA_Type','In_Stream','Subwatershed']

reorder_fields(temp + r"\LinkstoPoint",temp + r"\LinkstoPoint_reorder",reorder,add_missing = False)
reorder_fields(temp + r"\DME_nodes",temp + r"\DME_nodes_reorder",reorder,add_missing = False)
reorder_fields(temp + r"\private",temp + r"\private_reorder",reorder,add_missing = False)
reorder_fields(temp + r"\ecoroofs",temp + r"\ecoroofs_reorder",reorder,add_missing = False)

#merge feature classes
addMessage("Merging source features into one inventory")
merge_input = [temp + r"\LinkstoPoint_reorder",temp + r"\DME_nodes_reorder",temp + r"\private_reorder",temp + r"\ecoroofs_reorder"]
arcpy.Merge_management(merge_input,final_output + r"\BMP_inventory")

incrementField(final_output + r"\BMP_points")
