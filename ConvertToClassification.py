import ifcopenshell
import ifcopenshell.util.date

def convert_to_classification(file, model, pSetName):

    version = model.schema
    owner_history = model.by_type("IfcOwnerHistory")[0]
    project = model.by_type("IfcProject")[0]

    # Get all IfcPropertySet objects
    property_sets = model.by_type("IfcPropertySet")

    property_sets_classification = []
    removable = set()
    for property_set in property_sets:
        # if property_set.Name.startswith(pSetName):
        if property_set.Name in pSetName:
            property_sets_classification.append(property_set)


    for property_set in property_sets_classification:
        entities = []
        catalogAttr = {}
        classAttr = {} 
        relDefinesByProperties = []
        
        if version == "IFC2X3":
            relDefinesByProperties = property_set.PropertyDefinitionOf
        else:
            relDefinesByProperties = property_set.DefinesOccurrence
        for relDefinesByProperty in relDefinesByProperties:
            objects = relDefinesByProperty.RelatedObjects
            for obj in objects:
                entities.append(obj)
            removable.add(relDefinesByProperty)
                
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
                catalogAttr.get('Specification', None), 
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
            
            relClassClass = model.createIfcRelAssociatesClassification(
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                [project],
                classification
            )
        
        relClassRef = model.createIfcRelAssociatesClassification(
            ifcopenshell.guid.new(),
            owner_history,
            None,
            None,
            entities,
            reference
        )
    for obj in removable:
        model.remove(obj)
        
    model.write(file.replace('.ifc','') + "_with_classification.ifc")
    return "Conversion successful!"