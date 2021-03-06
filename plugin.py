import os
import sys

from pymxs import runtime as rt

sys.path.append(os.path.realpath(os.path.dirname(__file__)))
from yafe.io import BinaryStream, Endian, Structure
from yafe.fbn import FbnBinary
from yafe.structs.fbn import *

Y_TO_Z_UP_MATRIX = rt.Matrix3(rt.Point3(1,  0,  0), # x=x
                              rt.Point3(0,  0,  1), # y=z
                              rt.Point3(0, -1,  0), # z=-y
                              rt.Point3(0,  0,  0))

Z_TO_Y_UP_MATRIX = rt.Matrix3(rt.Point3(1,  0,  0), # x=x
                              rt.Point3(0,  0, -1), # y=-z
                              rt.Point3(0,  1,  0), # z=y
                              rt.Point3(0,  0,  0))

HANDLE_EXCEPTIONS = False

FBN_BLOCK_NAMES = {
    0x46424E30: 'header',
    1: 'triggers',
    4: 'entrances',
    5: 'hitdefs',
    14: 'npcs',
    19: 'triggers2',
    22: 'triggers3'
}

FBN_ENTRY_NAMES = {
    1: 'trigger_{index}',
    4: 'entrance_{id}',
    5: 'hit_{index}',
    14: 'npc_{id}',
    19: 'trigger2_{index}',
    22: 'trigger3_{index}'
}

# red green blue white black orange yellow brown gray 
FBN_BLOCK_COLOR = {
    1: rt.yellow,
    4: rt.green,
    5: rt.blue,
    14: rt.orange,
    19: rt.brown,
    22: rt.red,
        
    2:rt.color( 143.502, 192.052, 123.605),
    3:rt.color( 241.213, 189.81, 150.512),
    6:rt.color( 175.058, 94.528, 245.724),
    7:rt.color( 56.4881, 236.73, 9.59245),
    8:rt.color( 59.8833, 75.1598, 249.317),
    9:rt.color( 40.578 ,155.731, 156.499),
    10:rt.color( 76.9536, 141.077, 103.014),
    11:rt.color( 102.925, 17.0186, 33.5135),
    12:rt.color( 117.387, 56.3173, 216.853),
    13:rt.color( 232.425, 166.779, 125.757),
    15:rt.color( 240.711, 156.179, 193.649),
    16:rt.color( 212.046, 17.9807, 19.0009),
    17:rt.color( 42.9469, 18.3089, 196.639),
    18:rt.color( 206.483, 140.258, 23.8223),
    20:rt.color( 94.7837, 213.956, 165.767),
    21:rt.color( 35.0486, 198.158, 191.938),
    23:rt.color( 115.485, 69.6867, 77.3154),
    24:rt.color( 101.416, 203.023, 168.523),
    25:rt.color( 237.34, 237.202 ,166.125),
    26:rt.color( 95.2194, 92.7938, 187.842),
    27:rt.color( 251.007, 104.343, 60.597),
    28:rt.color( 231.905, 87.1817, 159.253),
    29:rt.color( 239.39, 201.597, 246.595),
    30:rt.color( 194.821, 50.4032 ,84.8526),
}

gCustomAttributeCache = dict()
gFlipUpAxis = True
gFbnHelper = None
gFbnBlockHelpers = dict()

def getScriptDir():
    return os.path.dirname(os.path.realpath(__file__))

def withExceptionHandler( func, *args ):
    if HANDLE_EXCEPTIONS:
        import traceback
        try:
            func( *args )
        except Exception as e:
            rt.messageBox(''.join(traceback.format_exception(None, e, e.__traceback__)), title='Error')
    else:
        func( *args )

def selectOpenFile( category, ext ):
    return rt.getOpenFileName(
        caption=("Open " + category + " file"),
        types=( category + " (*." + ext + ")|*." + ext ),
        historyCategory=( category + " Object Presets" ) )
    
def runMaxScriptFile( name ):
    rt.fileIn( getScriptDir() + '/maxscript/' + name  )
   
def getFbnBlockName( type ):
    if type in FBN_BLOCK_NAMES:
        return FBN_BLOCK_NAMES[type]
    else:
        return 'block_' + str( type )
        
def getFbnBlockColor( type ):
    if type in FBN_BLOCK_COLOR:
        return FBN_BLOCK_COLOR[type]
    else:
        return rt.green
    
def loadFile( path, endian, type, cb ):
    if os.path.exists( path ):
        with BinaryStream.openReadFile( path, endian ) as stream:
            inst = type.read( stream )
            cb( inst, path )
            
def createHelper( parent, name, pos, rot, color ):
    helper = rt.Point()
    if rot != None:
        if not hasattr( rot, 'W' ):
            helper.rotation = rt.Quat( rot.X, rot.Y, rot.Z, 1 ) 
        else:
            helper.rotation = rt.Quat( rot.X, rot.Y, rot.Z, rot.W )
    if pos != None:
        helper.pos = rt.Point3( pos.X, pos.Y, pos.Z )
    helper.name = name
    helper.parent = parent
    helper.scale = rt.Point3( 4, 4, 4 )
    helper.wirecolor = color
    
    global gFlipUpAxis
    if gFlipUpAxis:
        helper.transform *= Y_TO_Z_UP_MATRIX
    
    return helper
    
def getMaxscriptType( field ):
    typeName = field.type.__qualname__
    if typeName in ["S8", "U8", "S16", "U16", "S32", "U32", "S64", "U64"]:
        return "#integer"
    if typeName in ["F32"]:
        return "#float"
    raise NotImplementedError(typeName)
    
def getMaxscriptControl( field ):
    return "spinner"

# iterates all fields of an object resulting in a flat list
def iterObjectFields( obj, parentObj=None, field=None, path=None, elementIndex=None ):
    if hasattr( obj, '_fields' ):
        for field in obj._fields:
            val = getattr( obj, field.name )
            fieldPath = path + "." + field.name if path != None else field.name
            
            if isinstance( val, Structure ):
                # collapse struct
                yield from iterObjectFields( val, parentObj=obj, field=field, path=fieldPath )
            elif isinstance( val, list ):
                # skip variable arrays
                if not field.isFixedArray():
                    continue
                    
                # generate fixed array
                for i, item in enumerate( val ):
                    yield from iterObjectFields( item, parentObj=obj, field=field, path=f"{fieldPath}[{i}]", elementIndex=i )
            else:
                yield from iterObjectFields( val, parentObj=obj, field=field, path=fieldPath )
    else:
        # terminal node
        yield parentObj, obj, field, path, elementIndex
        
def genCustomAttributesFields( obj ):
    s = ''
    for parentObj, val, field, path, elementIndex in iterObjectFields( obj ):
        varName = "_" + path.replace(".", "_").replace("[", "_").replace("]", "_")
        s += f"      {varName} type:{getMaxscriptType(field)} ui:ui{varName}\n"
    return s

def genCustomAttributesRolloutFields( obj ):
    s = ''
    for parentObj, val, field, path, elementIndex in iterObjectFields( obj ):
        varName = "_" + path.replace(".", "_").replace("[", "_").replace("]", "_")
        dispName = path
        s += f'      label lbl{varName} "{dispName}" across:2 align:#left\n'
        s += f'      {getMaxscriptControl(field)} ui{varName} "" type:{getMaxscriptType(field)} across:2 offset:[16,0] width:128 range:[-4294967296,4294967296,0] align:#left\n' 
    return s
        
def assignCustomAttributesFromObject( obj, attribData ):
    for parentObj, val, field, path, elementIndex in iterObjectFields( obj ):
        varName = "_" + path.replace(".", "_").replace("[", "_").replace("]", "_")
        assert( hasattr( attribData, varName ) )
        #print( attribData, varName, val )
        setattr( attribData, varName, val )

def assignObjectFromCustomAttributes( obj, attribData ):
    for parentObj, val, field, path, elementIndex in iterObjectFields( obj ):
        #print( parentObj, val, field, path, field.name )
        varName = "_" + path.replace(".", "_").replace("[", "_").replace("]", "_")
        attribVal = getattr( attribData, varName )
        assert( hasattr( parentObj, field.name ) )
        
        if not isinstance( attribVal, field.getUnderlyingType() ):
            # try to convert to underlying type
            attribVal = field.getUnderlyingType()( attribVal )
        
        if elementIndex != None:
            # set array element value
            arr = getattr( parentObj, field.name )
            arr[ elementIndex ] = attribVal
            setattr( parentObj, field.name, arr )
            
        else:
            # set direct value
            setattr( parentObj, field.name, attribVal )

def genCustomAttributes( entry ):
    global gCustomAttributeCache
    
    typeName = entry.__class__.__name__
    if typeName in gCustomAttributeCache:
        return gCustomAttributeCache[typeName]
    else:
        s = f'attributes {typeName}Attributes (\n'
        s += "    parameters main rollout:params (\n"
        s += genCustomAttributesFields( entry )
        s += "    )\n"
        
        s += f'    rollout params "{typeName} Properties" (\n'
        s += genCustomAttributesRolloutFields( entry )
        s += "    )\n"
        s += ")\n"
        gCustomAttributeCache[typeName] = s
        print( s )
        return s
    return s
    
def getObjectCustomAttributes( obj, node ):
    typeName = obj.__class__.__name__
    return getattr( node, typeName + "Attributes" )

def getFbnEntryName( block, entry, index, id ):
    if block.Type in FBN_ENTRY_NAMES:
        return FBN_ENTRY_NAMES[block.Type].replace("{id}", str(id)).replace("{index}", str(index))
    else:
        return f'block_{block.Type}_{index}'
        
def addCustomAttributes( obj, node ):
    rt.custAttributes.add( node, rt.execute( genCustomAttributes( obj ) ) )
    assignCustomAttributesFromObject( obj, getObjectCustomAttributes( obj, node ) )
    
def createDefaultBlockEntryHelper( block, blockHelper, entry, i, color ):
    pos = None 
    rot = None
    id = None
    if hasattr( entry, 'Position' ):
        pos = entry.Position
    if hasattr( entry, 'Rotation' ):
        rot = entry.Rotation
    if hasattr( entry, 'Id' ):
        id = entry.Id
    
    entryHelper = createHelper( blockHelper, getFbnEntryName( block, entry, i, id ), pos, rot, color )
    addCustomAttributes( entry, entryHelper )
    return entryHelper
    
def importFbn( path ):
    fbn = None
    with BinaryStream.openReadFile( path, Endian.BIG ) as stream:
        fbn = FbnBinary.read( stream )
    isHtb = len( fbn.blocks ) == 1 and fbn.blocks[0][0].Type == 5
    
    # create FBN helper
    global gFbnHelper
    global gFbnBlockHelpers
    gFbnHelper = createHelper( None, os.path.basename( path ), None, None, rt.green )
    
    for block, entries in fbn.blocks:            
        # create helper for each block
        color = getFbnBlockColor( block.Type )
        blockHelper = createHelper( gFbnHelper, getFbnBlockName( block.Type ), None, None, color )
        addCustomAttributes( block, blockHelper )
        
        if block.ListOffset == 0:
            # empty
            continue
                
        if block.Type in [1, 19, 22]: # trigger volumes
            for i, entry in enumerate( entries ):
                triggerHelper = createHelper( blockHelper, getFbnEntryName( block, entry, i, None ), entry.Center, None, color )
                addCustomAttributes( entry, triggerHelper )
        elif block.Type in [5]: # htb hit def
            # TODO wont work if block node is renamed
            triggerBlockHelper = rt.getNodeByName( FBN_BLOCK_NAMES[1] )
            
            for i, entry in enumerate( entries ):
                # try to parent to trigger if possible
                if triggerBlockHelper != None:
                    try:
                        triggerBlockEntryHelper = triggerBlockHelper.children[i]
                        entryHelper = createDefaultBlockEntryHelper( block, blockHelper, entry, i, color )
                        #entryHelper.parent = triggerBlockEntryHelper
                        entryHelper.transform = triggerBlockEntryHelper.transform
                    except:
                        createDefaultBlockEntryHelper( block, blockHelper, entry, i, color )
                else:
                    createDefaultBlockEntryHelper( block, blockHelper, entry, i, color )
            
        elif block.Type in [11]: # dungeon thing
            for i, entry in enumerate( entries ):
                entryHelper = createHelper( blockHelper, getFbnEntryName( block, entry, i, None ), None, None, color )
                addCustomAttributes( entry, entryHelper )
                
                # create sub entry dummies
                for j in range( 0, entry.EntryCount ):
                    subEntryHelper = createHelper( entryHelper, f"{entryHelper.name}_{j}", None, None, color )
                    addCustomAttributes( entry.Entries[j], subEntryHelper )
        elif block.Type in [14]: # npcs
            for i, entry in enumerate( entries ):
                npcHelper = createHelper( blockHelper, getFbnEntryName( block, entry, i, entry.Id ), entry.PathNodes[0], None, color )
                addCustomAttributes( entry, npcHelper )
                
                for j in range( 1, entry.PathNodeCount ):
                    pathNodeHelper = createHelper( npcHelper, f"npc_{entry.Id}_pathnode_{j}", entry.PathNodes[j], None, color )
        else:
            # handle entry generically
            for i, entry in enumerate( entries ):
                createDefaultBlockEntryHelper( block, blockHelper, entry, i, color )
                
def _convertPoint3ToVector3( v ):
    res = Vector3()
    res.X = v[0]
    res.Y = v[1]
    res.Z = v[2]
    return res
    
def _convertQuatToQuaternion( v ):
    res = Quaternion()
    res.X = v[0]
    res.Y = v[1]
    res.Z = v[2]
    res.W = v[3]
    return res

def getHelperPositionVector3( helper ):
    tfm = rt.copy( helper.transform )
    
    global gFlipUpAxis
    if gFlipUpAxis:
        tfm *= Z_TO_Y_UP_MATRIX
        
    return _convertPoint3ToVector3( tfm.translationpart )
    
def getHelperRotationVector3( helper ):
    tfm = rt.copy( helper.transform )
    
    global gFlipUpAxis
    if gFlipUpAxis:
        tfm *= Z_TO_Y_UP_MATRIX
        
    return _convertPoint3ToVector3( tfm.rotationpart )
    
def getHelperRotationQuat( helper ):
    tfm = rt.copy( helper.transform )
    
    global gFlipUpAxis
    if gFlipUpAxis:
        tfm *= Z_TO_Y_UP_MATRIX
        
    return _convertQuatToQuaternion( tfm.rotationpart )
            
def exportFbn( path ):
    print( f'exporting FBN to {path}' )
    fbnHelper = rt.selection[0]
    print( f'FBN root: {fbnHelper}' )
    
    fbn = FbnBinary()
    
    # each block will be a child of the fbn helper node
    for blockHelper in fbnHelper.children:
        print(f'exporting block helper: {blockHelper}')
        
        # assign custom attribute values to block
        block = FbnBlock()
        entries = None
        assignObjectFromCustomAttributes( block, blockHelper )
        
        # collect the list items, if any
        if block.Type in [1, 19, 22]: # trigger volumes
            entries = []
            for triggerHelper in blockHelper.children:
                trigger = FbnTriggerVolume()
                assignObjectFromCustomAttributes( trigger, triggerHelper )
                # TODO proper handling
                trigger.Center = getHelperPositionVector3( triggerHelper )
                entries.append( trigger )
        elif block.Type in [11]: # dungeon thing
            entries = []
            for entryHelper in blockHelper.children:
                entry = FbnBlock11Entry()
                assignObjectFromCustomAttributes( entry, entryHelper )
                
                # collect sub entries
                for subEntryHelper in entryHelper.children:
                    subEntry = FbnBlock11SubEntry()
                    assignObjectFromCustomAttributes( subEntry, subEntryHelper )
                    entry.Entries.append( subEntry )
                    
                entry.EntryCount = len(entry.Entries)
                entries.append( entry )
        elif block.Type in [14]: # npcs
            entries = []
            for npcHelper in blockHelper.children:
                npc = FbnNpc()
                assignObjectFromCustomAttributes( npc, npcHelper )
                
                # create initial path node (base position)
                npc.PathNodes.append( getHelperPositionVector3( npcHelper ) )

                # create path nodes
                for pathNodeHelper in npcHelper.children:
                    npc.PathNodes.append( getHelperPositionVector3( pathNodeHelper ) )
                    
                # recalc node count
                npc.PathNodeCount = len( npc.PathNodes )
                    
                entries.append( npc )
        else:
            entries = []
            for entryHelper in blockHelper.children:
                entry = FbnBinary.BLOCK_MAP[block.Type]()
                assignObjectFromCustomAttributes( entry, entryHelper )
                if hasattr( entry, "Position" ):
                    entry.Position = getHelperPositionVector3( entryHelper )
                if hasattr( entry, 'Rotation' ):
                    if isinstance( entry.Rotation, Vector3 ):
                        entry.rotation = getHelperRotationVector3( entryHelper )
                    elif isinstance( entry.rotation, Quaternion ):
                        entry.rotation = getHelperRotationQuat( entryHelper )
                    else:
                        raise Exception( "Unhandled entry rotation data type" )
                entries.append( entry )  
        
        fbn.blocks.append( ( block, entries ) )
        
    # write fbn
    with BinaryStream( endian=Endian.BIG ) as stream:
        fbn.write( stream )
        with open( path, "wb" ) as f:
            print( f'writing to file {path}' )
            f.write( stream.getBuffer() )
            
    print( 'done' )
        
   
class yafeAboutRollout:
    @staticmethod
    def getMxsVar():
        return rt.yafeAboutRollout
    
    @staticmethod
    def loadConfig():
        pass

class yafeIORollout:
    @staticmethod
    def getMxsVar():
        return rt.yafeIORollout
    
    @staticmethod
    def loadConfig():
        global gFlipUpAxis
        yafeIORollout.getMxsVar().chkFlip.checked = gFlipUpAxis
    
    @staticmethod
    def btnImportPressed():
        filePath = rt.getOpenFileName(
            caption=(f"Open Persona 5 FBN/HTB file"),
            types=( "Persona 5 FBN (*.fbn)|*.fbn|Persona 5 HTB (*.htb)|*.htb" ),
            historyCategory=( "yafe import" ) )
        
        if filePath != None and os.path.exists( filePath ):
            withExceptionHandler( importFbn, filePath )
    
    @staticmethod
    def btnExportPressed():
        if len(rt.selection) == 0:
            rt.messageBox( "FBN root object not selected", title="Error", beep=True )
            return
        
        filePath = rt.getSaveFileName(
            caption=(f"Save Persona 5 FBN/HTB file"),
            types=( "Persona 5 FBN (*.fbn)|*.fbn|Persona 5 HTB (*.htb)|*.htb" ),
            historyCategory=( "yafe export" ) )
        
        if filePath != None:
            withExceptionHandler( exportFbn, filePath )
            
    @staticmethod
    def chkFlipChanged( state ):
        global gFlipUpAxis
        gFlipUpAxis = state
            
def createMainWindow():
    # get coords of window if it's already opened
    x = 30
    y = 100
    w = 250
    h = 700
    
    # ensure a variable exists even if it hasnt been created yet
    rt.execute( 'g_yafeWindow2 = g_yafeWindow' )
    if rt.g_yafeWindow2 != None:
        x = rt.g_yafeWindow2.pos.x
        y = rt.g_yafeWindow2.pos.y
        w = rt.g_yafeWindow2.size.x
        h = rt.g_yafeWindow2.size.y
        rt.closeRolloutFloater( rt.g_yafeWindow2 )
        
    # create plugin window
    rt.g_yafeWindow = rt.newRolloutFloater( "yafe plugin", w, h, x, y )
    rollouts = [yafeAboutRollout, yafeIORollout]
    
    for rollout in rollouts:
        rt.addRollout( rollout.getMxsVar(), rt.g_yafeWindow )
        rollout.loadConfig()
        
def attachDebugger():
    try:
        import ptvsd
        print( ptvsd.enable_attach() )
    except:
        print('failed to attach debugger')
    
def main():
    rt.clearListener()
    attachDebugger()
    runMaxScriptFile( 'rollouts.ms' )
    runMaxScriptFile( 'customattributes.ms' )
    createMainWindow()
 

if __name__ == '__main__':
    main()