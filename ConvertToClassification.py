import ifcopenshell
import ifcopenshell.util.date

def convert_to_classification(file, model, pSetName):

    try:
        version = model.schema
        owner_history = model.by_type("IfcOwnerHistory")[0]
        project = model.by_type("IfcProject")[0]

        # Get all IfcPropertySet objects
        property_sets = model.by_type("IfcPropertySet")

        property_sets_classification = []
        removable = set()
        
        # find all IfcPropertySets with the given names
        for property_set in property_sets:
            if property_set.Name in pSetName:
                property_sets_classification.append(property_set)

        # for each IfcPropertySet create a new IfcClassification and IfcClassificationReference
        for property_set in property_sets_classification:
            entities = []
            catalogAttr = {}
            classAttr = {} 
            relDefinesByProperties = []
            
            # get all related entities
            if version == "IFC2X3":
                relDefinesByProperties = property_set.PropertyDefinitionOf
            else:
                relDefinesByProperties = property_set.DefinesOccurrence
            for relDefinesByProperty in relDefinesByProperties:
                objects = relDefinesByProperty.RelatedObjects
                for obj in objects:
                    entities.append(obj)
                removable.add(relDefinesByProperty)
            
            # get all properties of the IfcPropertySet      
            properties = property_set.HasProperties
            for prop in properties:
                if prop.is_a("IfcPropertySingleValue"):
                    if prop.Name.startswith("Catalog"):
                        catName = prop.Name.replace("Catalog", "")
                        catalogAttr[catName] = prop.NominalValue.wrappedValue
                    elif prop.Name.startswith("Class"):
                        className = prop.Name.replace("Class", "")
                        classAttr[className] = prop.NominalValue.wrappedValue
                    else:
                        print("Unknown property: ", prop.Name)
                removable.add(prop)
            removable.add(property_set)
            
            # create IfcClassification and IfcClassificationReference
            if version == "IFC2X3":
                dates = ifcopenshell.util.date.datetime2ifc(catalogAttr.get('EditionDate', None), 'IfcCalendarDate')
                caledarDate = model.createIfcCalendarDate(dates['DayComponent'], dates['MonthComponent'], dates['YearComponent'])
                classification = model.createIfcClassification(
                    catalogAttr.get('Source', None), 
                    catalogAttr.get('Edition', None), 
                    caledarDate, 
                    catalogAttr.get('Name')
                )  
                reference = model.createIfcClassificationReference(
                    classAttr.get('Location', None),
                    classAttr.get('Identification', None),
                    classAttr.get('Name', None),
                    classification  
            )    
            else:
                classification = model.createIfcClassification(
                    catalogAttr.get('Source', None), 
                    catalogAttr.get('Edition', None), 
                    catalogAttr.get('EditionDate', None), 
                    catalogAttr.get('Name'), 
                    catalogAttr.get('Description', None), 
                    catalogAttr.get('Specification', None), # IFC 4.3
                    catalogAttr.get('Location', None), # IFC 4
                    catalogAttr.get('ReferenceToken', None)
                )
                reference = model.createIfcClassificationReference(
                    classAttr.get('Location', None),
                    classAttr.get('Identification', None),
                    classAttr.get('Name', None),
                    classification,
                    classAttr.get('Description', None),
                    classAttr.get('Sort', None)   
                )    
                
                # create IfcRelAssociatesClassification between IfcProject and IfcClassification, not in IFC 2x3 specified
                model.createIfcRelAssociatesClassification(
                    ifcopenshell.guid.new(),
                    owner_history,
                    None,
                    None,
                    [project],
                    classification
                )
            
            # create IfcRelAssociatesClassification between IfcClassificationReference and related entities
            model.createIfcRelAssociatesClassification(
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                entities,
                reference
            )
            
        # remove all IfcPropertySets
        for obj in removable:
            model.remove(obj)
            
        model.write(file.replace('.ifc','') + "_with_classification.ifc")
        return "Conversion successful!"
    
    except Exception as e:
        return str(e)