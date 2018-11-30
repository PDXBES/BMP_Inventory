#-------------------------------------------------------------------------------
# Name:        tools
# Purpose:
#
# Author:      DASHNEY
#
# Created:     02/02/2015

#-------------------------------------------------------------------------------

import arcpy
from utilities import addMessage

def add_StandardFields(input):

    addMessage("Adding standard fields to " + input)
    arcpy.AddField_management(input,"UID","LONG")
    arcpy.AddField_management(input,"Original_ID","TEXT","","",20)
    arcpy.AddField_management(input,"As_Built","TEXT","","",10)
    arcpy.AddField_management(input,"InstallDate","DATE")
    arcpy.AddField_management(input,"MS4","SHORT")
    arcpy.AddField_management(input,"Data_Source","TEXT","","",25)
    arcpy.AddField_management(input,"Original_Type","TEXT","","",35)
    arcpy.AddField_management(input,"Gen_Type","TEXT","","",35)
    arcpy.AddField_management(input,"ACWA_ID","LONG")
    arcpy.AddField_management(input,"ACWA_Type","TEXT","","",50)
    arcpy.AddField_management(input,"In_Stream","LONG")
    arcpy.AddField_management(input,"Nearest_Hansen","TEXT","","",10)
    arcpy.AddField_management(input,"Subwatershed","TEXT","","",25)

def incrementField(input):

    addMessage("Populating unique IDs for " + input)
    with arcpy.da.UpdateCursor(input, "UID") as rows:
        for i, row in enumerate(rows, 1):
            row[0] = i
            rows.updateRow(row)

def fillField(input,field,value):

    #value supplied must match data type of existing field

    addMessage("Populating the " + field + " field for " +  input)
    with arcpy.da.UpdateCursor(input, field) as cursor:
        for row in cursor:
            row[0] = value
            cursor.updateRow(row)

def fillField_Conditional(input,field,value):

    #value supplied must match data type of existing field

    addMessage("Populating the " + field + " field for " +  input)
    with arcpy.da.UpdateCursor(input, field) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = value
                cursor.updateRow(row)

def fillField_fromAnother(input,targetField,sourceField):

    addMessage("Populating the " + targetField + " field for " +  input)
    with arcpy.da.UpdateCursor(input, [targetField, sourceField]) as cursor:
        for row in cursor:
            row[0] = row[1]
            cursor.updateRow(row)

def fillField_ifOverlap(input, overlapFC, targetField, value):

    addMessage("Populating the " + targetField + " field for " +  input)
    input_layer = "input_layer"
    arcpy.MakeFeatureLayer_management(input, input_layer)
    selection = arcpy.SelectLayerByLocation_management(input_layer,"INTERSECT",overlapFC)
    arcpy.CalculateField_management(selection,targetField,value)

def calcField_fromOverlap(input,overlapFC,targetField,sourceField):

    addMessage("Populating the " + targetField + " field for " +  input)
    result = arcpy.Intersect_analysis([input,overlapFC],"in_memory\sect_result","NO_FID","","POINT")
    values={}
    with arcpy.da.SearchCursor(result,["UID",sourceField]) as cursor:
        for row in cursor:
            if row[0] != None:
                values[row[0]] = row[1]

    with arcpy.da.UpdateCursor(input, ["UID", targetField]) as cursor:
        for row in cursor:
            if row[0] in values:
                if values[row[0]] != None:
                    row[1] = values[row[0]]
                cursor.updateRow(row)

def calcField_withinDistance(inputFC,selectFC,criteria,distance,targetField,fillValue):

    addMessage("Populating the " + targetField + " field for " +  inputFC)
    select_input = "select_put"
    select_input = arcpy.MakeFeatureLayer_management(inputFC,select_input,criteria)
    #att_selection = arcpy.SelectLayerByAttribute_management(select_input,"NEW_SELECTION",criteria)
    loc_selection = arcpy.SelectLayerByLocation_management(select_input,"INTERSECT",selectFC,distance,"SUBSET_SELECTION")
    arcpy.CalculateField_management(loc_selection,targetField,fillValue)

def fillField_fromDict(inputFC,dictionary,sourceField,targetField):

    addMessage("Populating the " + targetField + " field for " +  inputFC)
    with arcpy.da.UpdateCursor(inputFC,[sourceField,targetField]) as rows:
        for row in rows:
            for key,value in dictionary.items():
                if row[0] == key:
                    row[1] = value
                #elif row[0] is None:
                    #row[1] = 9999
                rows.updateRow(row)
