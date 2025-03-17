import ifcopenshell
import ifcopenshell.util.date
import ifcopenshell.util.element

# Convert IfcClassification to IfcPropertySet
def convert_to_property_set(file, model, pSetNameType):

    try:
        version = model.schema
        owner_history = model.by_type("IfcOwnerHistory")[0]

        # find all IfcClassificationReferences
        references = model.by_type("IfcClassificationReference")

        removable = set()
        changedEntities = []

        # for each IfcClassificationReference create a new IfcPropertySet 
        for reference in references:
            pSetName = pSetNameType
            properties = {}
            attr = reference.__dict__
            
            # get all attributes of the IfcClassificationReference
            for key in attr:
                if key == 'id' or key == 'type' or key == 'GlobalId' or key == 'OwnerHistory':
                    continue
                elif key == 'ReferencedSource':
                    classification = attr.get(key)
                    if classification is not None and classification.is_a("IfcClassification"):
                        properties['Class'+key] = classification.Name
                        catalogAttr = classification.__dict__
                        
                        # get all attributes of the IfcClassification
                        for k in catalogAttr:
                            if k == 'id' or k == 'type' or k == 'GlobalId' or k == 'OwnerHistory':
                                continue
                            elif k == 'EditionDate' and version == "IFC2X3":
                                date = ifcopenshell.util.date.ifc2datetime(catalogAttr.get(k))
                                if date is not None:
                                    properties['Catalog'+k] = date.strftime("%Y-%m-%d")
                                removable.add(catalogAttr.get(k))
                            else:
                                val = catalogAttr.get(k)
                                if val is not None:
                                    properties['Catalog'+k] = val
                        removable.add(classification)
                        if version != "IFC2X3":
                            removable.add(classification.ClassificationForObjects[0])
                else:
                    value = attr.get(key)
                    if key == 'Identification' and pSetName == 'GenerateNames' and value is not None:
                        val = value.split('/')
                        l = len(val)
                        try:
                            pSetName = 'bSD_' + val[l-4] + '_' + val[l-3]
                        except:
                            pSetName = 'bSD_' + attr.get("Name")
                    if value is not None:
                        properties['Class'+key] = value
            removable.add(reference)
            
            # find all related entities for IfcClassificationReference
            entities = []
            relAssoc = []
            if version == "IFC2X3":
                rels = model.by_type('IfcRelAssociatesClassification')
                for rel in rels:
                    if rel.RelatingClassification == reference:
                        relAssoc.append(rel)
            else:
                relAssoc = reference.ClassificationRefForObjects
                
            for rel in relAssoc:
                entities.extend(rel.RelatedObjects)
                removable.add(rel)
            
            # check if the property set name already exists for an entity
            count = 0
            for e in entities:
                psets = ifcopenshell.util.element.get_psets(e, psets_only=True)
                c = 0
                for pset in psets:
                    if pset == pSetName:
                        c += 1
                if c > count:
                    count = c

            ifcPsetName = pSetName
            if count > 0:
                ifcPsetName = pSetName + '_' + str(count)
                
            # create IfcPropertySingleValues and IfcPropertySet
            ifcProperties = []
            for key in properties:
                ifcProperties.append(model.createIfcPropertySingleValue(key, None, model.createIfcText(properties[key]), None))
            pSet = model.createIfcPropertySet(
                ifcopenshell.guid.new(),
                owner_history,
                ifcPsetName,
                None,
                ifcProperties
            )
                
            # create IfcRelDefinesByProperties
            model.createIfcRelDefinesByProperties(
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                entities,
                pSet
            )
            
            changedEntities.extend(entities)

        # remove all IfcClassificationReferences
        for obj in removable:
            model.remove(obj)
        
        model.write(file.replace('.ifc','') + "_with_propertyset.ifc")
        return "Conversion successful!"
    
    except Exception as e:
        return str(e)