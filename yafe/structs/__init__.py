import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/../../'))

from yafe.io import Field

class StructureDumper(object):
    TYPE_DICT = {
        "s8": ("S8", 1),
        "u8": ("U8", 1),
        "s16": ("S16", 2),
        "u16": ("U16", 2),
        "s32": ("S32", 4),
        "u32": ("U32", 4),
        "s64": ("S64", 8),
        "u64": ("U64", 8),
        "f32": ("F32", 4)
    }
    
    OVERRIDE_TYPES = {
        "IntFloat": 
"""
class IntFloat(yafe.io.Structure):
    _fields = [
        Field("Int", yafe.io.S32, offset=0)
        Field("Float", yafe.io.F32, offset=0)
    ]
""",
        "FbnBlock":
"""
class FbnBlock(Structure):
    _fields = [
        Field("Type", U32),
        Field("Field04", U32),
        Field("Size", U32),
        Field("ListOffset", U32),
        Field("List", FbnList)
    ]
"""
    }
    
    def __init__( self ):
        self.templateFiles = []
    
    def addTemplateFile( self, path ):
        self.templateFiles.append( path )

    def _templateTypeToCType( self, type ):
        if type in self.TYPE_DICT:
            return f"{self.TYPE_DICT[type][0]}"
        else:
            return type
        
    def _parse( self ):
        templateStructDefs = []
        
        localTypeDict = self.TYPE_DICT
        for filePath in self.templateFiles:
            with open( filePath ) as f:
                rawLine = f.readline()
                statements = rawLine.strip().split(';')
                insideStruct = False
                isUnion = False
                fields = []
                structDefs = []
                fieldOffset = None
                
                while rawLine != "":        
                    for statement in statements: 
                        tokens = statement.split( ' ' )
                        
                        if len(tokens) >= 2 and tokens[0] == 'typedef' and tokens[1] == 'struct':
                            # struct start
                            insideStruct = True
                        elif len(tokens) >= 2 and tokens[0] == 'typedef' and tokens[1] == 'union':
                            insideStruct = True
                            isUnion = True
                            fieldOffset = 0
                        elif len(tokens) >= 2 and tokens[0] == '}': 
                            if insideStruct:
                                if not tokens[1] in localTypeDict:
                                    localTypeDict[tokens[1]] = (tokens[1], fieldOffset)
                                structDefs.append((tokens[1], fields))
                            insideStruct = False
                            fields = []
                            fieldOffset = None
                        elif len(tokens) >= 2 and insideStruct:
                            tokenIndex = 0
                            if len(tokens) >= 3 and tokens[0] == 'struct':
                                tokenIndex += 1
                            
                            fieldType = tokens[tokenIndex]
                            fieldName = tokens[tokenIndex + 1]
                            fieldLength = '1'
                            
                            if '(' in fieldName:
                                continue
                            
                            if not fieldType in localTypeDict and not fieldType.startswith('Fbn'):
                                pass
                            else:
                                if '[' in fieldName:
                                    originalFieldName = fieldName
                                    fieldName = originalFieldName[:fieldName.index('[')]
                                    fieldLength = originalFieldName[originalFieldName.index('[')+1:].strip(']')
                                    if fieldLength.strip() == '':
                                        fieldLength = tokens[tokenIndex + 2]
                                fields.append(Field(fieldName, fieldType, fieldLength, fieldOffset))
                                #if not isUnion:
                                #    fieldOffset += localTypeDict[fieldType][1]
                                
                    rawLine = f.readline()        
                    statements = rawLine.strip().split(';')
                            
            templateStructDefs.append((filePath, structDefs))
        return templateStructDefs
                        
    def writePythonCode( self, path ):
        with open( path, "w" ) as f:
            f.write(f"from yafe.io import *\n")
            f.write("from typing import Any\n")
            for templateFilePath, structDefs in self._parse():
                f.write(f'# generated from {templateFilePath}\n')
                for structName, Fields in structDefs:
                    f.write(f'class {structName}(Structure):\n')
                    f.write(f"    _fields = [\n")
                    for field in Fields:
                        count = field.count
                        try:
                            int(count)
                        except:
                            count = f'"{count}"'
                        
                        f.write(f'        Field("{field.name}", {self._templateTypeToCType(field.type)}, count={count}, offset={field.offset}),\n')
                    f.write(f"    ]\n")
                    
                    f.write('    def __init__( self ):\n')
                    for field in Fields:
                        f.write(f'        self.{field.name} = None\n')
                    f.write('        super().__init__()\n')
                    f.write("\n")
    
if __name__ == '__main__':
    dumper = StructureDumper()
    dumper.addTemplateFile("X:/code/010-Editor-Templates/templates/p5_fbn.bt")
    dumper.writePythonCode( os.path.dirname(__file__) + '/fbn.py')