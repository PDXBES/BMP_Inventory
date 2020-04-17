#-------------------------------------------------------------------------------
# Name:        BMP_tools
# Purpose:     some geoprocessing tools to move field data from one fc to another using either attribute or spatial relationships
#
# Author:      DASHNEY
#
# Created:     02/02/2015

#-------------------------------------------------------------------------------

import arcpy
from utilities import addMessage

def add_StandardFields(input):

    # adds a set of fields, this is specific to the BMP inventory - could be made generic by looping through a list of info
    #addMessage("Adding standard fields to " + input)
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

    # for a given field, populates the field with an incrementing (n+1) set of values starting at 1 - can be used to create a unique ID field
    addMessage("Populating unique IDs for " + input)
    with arcpy.da.UpdateCursor(input, "UID") as rows:
        for i, row in enumerate(rows, 1):
            row[0] = i
            rows.updateRow(row)

def fillField(input,field,value):

    # fills a specified field with a specified, individual value
    #value supplied must match data type of existing field

    addMessage("Populating the " + field + " field for " +  input)
    with arcpy.da.UpdateCursor(input, field) as cursor:
        for row in cursor:
            row[0] = value
            cursor.updateRow(row)

def fillField_Conditional(input,field,new_value,criteria):

    # fills a specified field with a specified, individual value where any specified field meets a specified value
    # input value supplied must match data type of existing field

    addMessage("Populating the " + field + " field for " +  input)
    select_input = arcpy.MakeFeatureLayer_management(input,"select_input",criteria)
    with arcpy.da.UpdateCursor(select_input, field) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = value
                cursor.updateRow(row)

def fillField_fromAnother(input,targetField,sourceField):

    #fills field from another field within the same feature class
    addMessage("Populating the " + str(targetField) + " field for " +  str(input))
    with arcpy.da.UpdateCursor(input, [targetField, sourceField]) as cursor:
        for row in cursor:
            row[0] = row[1]
            cursor.updateRow(row)

def fillField_ifOverlap(input, overlapFC, targetField, value):

    #fills specified field with a specified, individual value where overlap exists between target and another fc
    # input value supplied must match data type of existing field

    addMessage("Populating the " + targetField + " field for " +  str(input))
    input_layer = "input_layer"
    arcpy.MakeFeatureLayer_management(input, input_layer)
    selection = arcpy.SelectLayerByLocation_management(input_layer,"INTERSECT",overlapFC)
    arcpy.CalculateField_management(selection,targetField,value)

def calcField_fromOverlap(input,overlapFC,targetField,sourceField):

    #fills field with values from another field where overlap exists
	#need to fix as it uses UID to join data - is not generic

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
    select_input = arcpy.MakeFeatureLayer_management(inputFC,"select_input",criteria)
    #att_selection = arcpy.SelectLayerByAttribute_management(select_input,"NEW_SELECTION",criteria)
    loc_selection = arcpy.SelectLayerByLocation_management(select_input,"INTERSECT",selectFC,distance,"SUBSET_SELECTION")
    arcpy.CalculateField_management(loc_selection,targetField,fillValue)

def fillField_fromDict(inputFC,dictionary,sourceField,targetField):

    addMessage("Populating the " + targetField + " field for " +  str(inputFC))
    with arcpy.da.UpdateCursor(inputFC,[sourceField,targetField]) as rows:
        for row in rows:
            for key,value in dictionary.items():
                if row[0] == key:
                    row[1] = value
                #elif row[0] is None:
                    #row[1] = 9999
                rows.updateRow(row)

def CopyFieldFromFeature(sourceFC,sourceID,sourceField,targetFC,targetID,targetField):

#copy value from a field in one feature class to another through an ID field link - used in place of a table join and field populate (faster)

    #print "Running : " + datetime.datetime.now().strftime('%x %X')
    addMessage("Copying field data from " + sourceFC + "to " + targetFC + "using the field: " + sourceID)

    values={}
    with arcpy.da.SearchCursor(sourceFC,[sourceID,sourceField]) as cursor:
        for row in cursor:
            values[row[0]] = row[1]

    with arcpy.da.UpdateCursor(targetFC,[targetID,targetField]) as cursor:
        for row in cursor:
            if row[0] in values:
                if values[row[0]] != None:
                    row[1] = values[row[0]]
                cursor.updateRow(row)
    print "Done: " + datetime.datetime.now().strftime('%x %X')
