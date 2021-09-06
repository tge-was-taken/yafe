import os
import sys
import re
from typing import List, Tuple
sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/../../'))

from yafe.io import Field

class Stmt(object):
    def __init__( self, text=None ):
        self.text = text
        
    def __repr__(self) -> str:
        return (self.__class__.__qualname__, self.text).__repr__()

class CallExpr(Stmt):
    def __init__( self, text=None, name=None, args=None ):
        super().__init__( text )
        self.name = name
        self.args = args
        
    def __repr__(self) -> str:
        return (self.__class__.__qualname__, self.name, self.args).__repr__()

class EnumMemberDef(Stmt):
    def __init__( self, text=None, name=None, value=None ):
        super().__init__( text )
        self.name = name
        self.value = value
        
    def __repr__(self) -> str:
        return (self.__class__.__qualname__, self.name, self.value).__repr__()

class FieldDef(Stmt):
    def __init__( self, text=None, type=None, name=None, count=None, bitsize=None ):
        super().__init__( text )
        self.type = type
        self.name = name
        self.count = count
        self.bitsize = bitsize
        
    def __repr__(self) -> str:
        return (self.__class__.__qualname__, self.type, self.name, self.count, self.bitsize).__repr__()

class TypeDef(Stmt):
    def __init__( self, text=None, qualifier=None, name=None, baseType=None ):
        super().__init__( text )
        self.qualifier = qualifier
        self.name = name
        self.baseType = baseType
        self.statements = []
        
    def __repr__(self) -> str:
        return (self.__class__.__qualname__, self.qualifier, self.name, self.baseType, self.statements).__repr__()

class TemplateParser(object):
    REGEX_TYPEDEF = re.compile(
r"""
\s*typedef\s+(?P<class>struct|union|enum)   # type qualifier
\s*(<(?P<baseType>\w+)>)?                   # enum base (underlying) type
\s*(\((?P<args>.*?)\))?                     # struct args
\s*{(?P<fields>.*?)}                        # type fields/body
\s*(?P<name>\w+)                            # type name
\s*(?P<tags><.+?>)?                         # 010 type tags
\s*;                                        # closing ; to make greedy matching body possible
""", re.M | re.S | re.X )
    REGEX_STRUCT_FIELD = re.compile(
r"""
^\s*((?P<storage>local)\s+?)?                       # storage qualifier
\s*((?P<qualifier>struct|enum|union)\s+?)?          # type qualifier
(?P<type>\w+)                                       # field type name
\s+?(?P<name>\w+)                                   # field name
\s*?(\[\s*?(?P<count>[\w\d]+?)\s*?\])?              # array length
(\s*:\s*(?P<bitsize>\d+))?.*?;                      # bit size (bitfield)
""", re.X)
    REGEX_ENUM_MEMBER = re.compile(
r"""
^\s*(?P<name>\w+)                           # member name
\s*=\s*                                     # = operator
(?P<value>\d+),?                            # member value
""", re.X)                  
    REGEX_CALL = re.compile(r"""(?P<name>\w+)\((?P<args>.+?)?\);""")
    
    
    def __init__( self ):
        self.knownTypes = ['s8', 's16', 's32', 'u8', 'u16', 'u32', 'f32', 'string']
    
    def parseFile( self, path ):
        fileText = None
        with open( path ) as f:
            fileText = f.read()
        
        typedefMatches = list(re.finditer( self.REGEX_TYPEDEF, fileText ))
        for typedefMatch in typedefMatches:
            self.knownTypes.append(typedefMatch.group("name"))
            
        typedefs = []    
        for typedefMatch in typedefMatches:
            klass = typedefMatch.group('class')
            name = typedefMatch.group('name')
            baseType = typedefMatch.group('baseType')
            fieldText = typedefMatch.group('fields')
            typedef = TypeDef( typedefMatch.string, klass, name, baseType )
            
            fieldLines = fieldText.splitlines()
            
            for fieldLine in fieldLines:
                if fieldLine.strip() == '':
                    continue
                
                if klass in ['struct', 'union']:
                    # parse fields
                    parsed = False
                    for field in re.finditer( self.REGEX_STRUCT_FIELD, fieldLine ):
                        if field.group('storage') == 'local':
                            continue
                        
                        typedef.statements.append(FieldDef( field.string, field.group('type'), field.group('name'), field.group('count'), field.group('bitsize')))
                        parsed = True
                        
                    if parsed:
                        continue
                        
                    for call in re.finditer( self.REGEX_CALL, fieldLine ):
                        typedef.statements.append(CallExpr( call.string, call.group('name'), call.group('args')))
                        parsed = True
                        
                    if parsed:
                        continue
                    
                    typedef.statements.append(Stmt( fieldLine ))
                elif klass == 'enum':
                    # parse members
                    parsed = False
                    for member in re.finditer( self.REGEX_ENUM_MEMBER, fieldLine ):
                        typedef.statements.append(EnumMemberDef(member.string, member.group('name'), member.group('value')))
                        parsed = True
                        
                    if parsed:
                        continue
                    
                    typedef.statements.append(Stmt( fieldLine ))
        
            typedefs.append( typedef )
            
        return typedefs
    

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
        
    def _parse( self ) -> List[Tuple[str, List[TypeDef]]]:
        parser = TemplateParser()
        typedefs = []
        for templateFile in self.templateFiles:
            typedefs.append( ( templateFile, parser.parseFile( templateFile ) ) )
        
        return typedefs
    
    def _writePythonCodeForType( self, f, typedefDict, typedef, excludedTypes ):
        if typedefDict[typedef.name][1]:
            # dont write if already written
            return
        
        typedefDict[typedef.name] = (typedef, True)
        
        excludedFields = dict()
        if typedef.name in excludedTypes:
            excludedFields = excludedTypes[typedef.name]
            if excludedFields == None:
                return
        
        if typedef.qualifier in ['struct', 'union']:            
            f.write(f'class {typedef.name}(Structure):\n')
            f.write(f"    _fields = [\n")
            endian = None
            for stmt in typedef.statements:
                if isinstance( stmt, FieldDef ):
                    field = stmt   
                    if field.name in excludedFields:
                        continue
                            
                    count = field.count
                    if count in ['', None]:
                        count = 1
                    
                    try:
                        int(count)
                    except:
                        count = f'"{count}"'
                        
                    offset = None
                    if typedef.qualifier == 'union':
                        offset = 0
                        
                    type = field.type
                    if type in typedefDict and typedefDict[type][0].qualifier == 'enum':
                        type = typedefDict[type][0].baseType
                    elif field.bitsize not in ['', None]:
                        # rewrite type
                        # assume multiple of 8
                        bitsize = int(field.bitsize)
                        if bitsize == 8:
                            type = 's8'
                        elif bitsize == 16:
                            type = 's16'
                        elif bitsize == 32:
                            type = 's32'
                        elif bitsize == 64:
                            type = 's64'
                        else:
                            raise NotImplementedError('non-multiple of 8 bit sizes not supported for bitfields')
                    
                    f.write(f'        Field("{field.name}", {self._templateTypeToCType(type)}, count={count}, offset={offset}, endian={endian}),\n')
                elif isinstance( stmt, CallExpr ):
                    if stmt.name == 'LittleEndian':
                        endian = 0
                    elif stmt.name == 'BigEndian':
                        endian = 1
                    
            f.write(f"    ]\n")
            
            f.write('    def __init__( self ):\n')
            for stmt in typedef.statements:
                if isinstance( stmt, FieldDef ):
                    field = stmt   
                    if field.name in excludedFields:
                        continue
                    
                    f.write(f'        self.{field.name} = None\n')
            f.write('        super().__init__()\n')
            f.write("\n")
                        
    def writePythonCode( self, path, excludedTypes ):
        with open( path, "w" ) as f:
            f.write(f"from yafe.io import *\n")
            f.write("from typing import Any\n")
            for templateFilePath, typedefs in self._parse():
                f.write(f'# generated from {templateFilePath}\n')
                
                typedefDict = dict()
                for typedef in typedefs:
                    typedefDict[typedef.name] = (typedef, False)
                    
                for typedef in typedefs:
                    for stmt in typedef.statements:
                        if isinstance( stmt, FieldDef ) and stmt.type in typedefDict and not typedefDict[stmt.type][1]:
                            # write dependency first
                            self._writePythonCodeForType( f, typedefDict, typedefDict[stmt.type][0], excludedTypes )
                    
                    self._writePythonCodeForType( f, typedefDict, typedef, excludedTypes )
    
if __name__ == '__main__':
    #parser = TemplateParser()
    #parser.parseFile( "X:/code/010-Editor-Templates/templates/p5_fbn.bt" )
    
    exclusions = {
        "FbnList": None, 
        "FbnBlock": ["List", "RawData"]
    }
    dumper = StructureDumper()
    dumper.addTemplateFile("X:/code/010-Editor-Templates/templates/p5_fbn.bt")
    dumper.writePythonCode( os.path.dirname(__file__) + '/fbn.py', exclusions )