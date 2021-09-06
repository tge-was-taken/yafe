from yafe.io import *
from typing import Any
# generated from X:/code/010-Editor-Templates/templates/p5_fbn.bt
class Vector3(Structure):
    _fields = [
        Field("X", F32, count=1, offset=None, endian=None),
        Field("Y", F32, count=1, offset=None, endian=None),
        Field("Z", F32, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.X = None
        self.Y = None
        self.Z = None
        super().__init__()

class Quaternion(Structure):
    _fields = [
        Field("X", F32, count=1, offset=None, endian=None),
        Field("Y", F32, count=1, offset=None, endian=None),
        Field("Z", F32, count=1, offset=None, endian=None),
        Field("W", F32, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.X = None
        self.Y = None
        self.Z = None
        self.W = None
        super().__init__()

class IntFloat(Structure):
    _fields = [
        Field("Int", S32, count=1, offset=0, endian=None),
        Field("Float", F32, count=1, offset=0, endian=None),
    ]
    def __init__( self ):
        self.Int = None
        self.Float = None
        super().__init__()

class FbnBlock(Structure):
    _fields = [
        Field("Type", S32, count=1, offset=None, endian=None),
        Field("Version", S32, count=1, offset=None, endian=None),
        Field("Size", S32, count=1, offset=None, endian=None),
        Field("ListOffset", S32, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Type = None
        self.Version = None
        self.Size = None
        self.ListOffset = None
        super().__init__()

class FbnTriggerVolume(Structure):
    _fields = [
        Field("Field00", S16, count=1, offset=None, endian=None),
        Field("Field02", S16, count=1, offset=None, endian=None),
        Field("Field04", S16, count=1, offset=None, endian=None),
        Field("Field06", S16, count=1, offset=None, endian=None),
        Field("Center", Vector3, count=1, offset=None, endian=None),
        Field("Field14", F32, count=1, offset=None, endian=None),
        Field("Field18", F32, count=1, offset=None, endian=None),
        Field("Field1C", F32, count=1, offset=None, endian=None),
        Field("Field20", F32, count=1, offset=None, endian=None),
        Field("Field24", F32, count=1, offset=None, endian=None),
        Field("Field28", F32, count=1, offset=None, endian=None),
        Field("BottomRight", Vector3, count=1, offset=None, endian=None),
        Field("TopRight", Vector3, count=1, offset=None, endian=None),
        Field("BottomLeft", Vector3, count=1, offset=None, endian=None),
        Field("TopLeft", Vector3, count=1, offset=None, endian=None),
        Field("Field5C", F32, count=1, offset=None, endian=None),
        Field("Field60", F32, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Field02 = None
        self.Field04 = None
        self.Field06 = None
        self.Center = None
        self.Field14 = None
        self.Field18 = None
        self.Field1C = None
        self.Field20 = None
        self.Field24 = None
        self.Field28 = None
        self.BottomRight = None
        self.TopRight = None
        self.BottomLeft = None
        self.TopLeft = None
        self.Field5C = None
        self.Field60 = None
        super().__init__()

class FbnEntrance(Structure):
    _fields = [
        Field("Field00", S32, count=1, offset=None, endian=None),
        Field("Field04", S32, count=1, offset=None, endian=None),
        Field("Position", Vector3, count=1, offset=None, endian=None),
        Field("Rotation", Vector3, count=1, offset=None, endian=None),
        Field("Id", S16, count=1, offset=None, endian=None),
        Field("Field22", S16, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Field04 = None
        self.Position = None
        self.Rotation = None
        self.Id = None
        self.Field22 = None
        super().__init__()

class FbnHitDefinitionTextIds(Structure):
    _fields = [
        Field("TitleTextId", S8, count=1, offset=None, endian=None),
        Field("SubTitleTextId", S8, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.TitleTextId = None
        self.SubTitleTextId = None
        super().__init__()

class FbnHitDefinition(Structure):
    _fields = [
        Field("BitFlags", S32, count=6, offset=None, endian=0),
        Field("Field18", S8, count=1, offset=None, endian=0),
        Field("PromptType", S8, count=1, offset=None, endian=0),
        Field("Text", FbnHitDefinitionTextIds, count=1, offset=None, endian=0),
        Field("ProcedureId", S16, count=1, offset=None, endian=0),
        Field("PromptSubType", S8, count=1, offset=None, endian=1),
        Field("Unused", S8, count=29, offset=None, endian=1),
    ]
    def __init__( self ):
        self.BitFlags = None
        self.Field18 = None
        self.PromptType = None
        self.Text = None
        self.ProcedureId = None
        self.PromptSubType = None
        self.Unused = None
        super().__init__()

class FbnBlock8Entry(Structure):
    _fields = [
        Field("Field00", S32, count=1, offset=None, endian=None),
        Field("Field04", S16, count=1, offset=None, endian=None),
        Field("Field06", S16, count=1, offset=None, endian=None),
        Field("Position", Vector3, count=1, offset=None, endian=None),
        Field("Field08", F32, count=5, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Field04 = None
        self.Field06 = None
        self.Position = None
        self.Field08 = None
        super().__init__()

class FbnBlock9Entry(Structure):
    _fields = [
        Field("Field00", S32, count=1, offset=None, endian=None),
        Field("Position", Vector3, count=1, offset=None, endian=None),
        Field("Field10", F32, count=4, offset=None, endian=None),
        Field("Field20", S16, count=1, offset=None, endian=None),
        Field("Field22", S16, count=1, offset=None, endian=None),
        Field("Field24", S16, count=1, offset=None, endian=None),
        Field("Field26", S16, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Position = None
        self.Field10 = None
        self.Field20 = None
        self.Field22 = None
        self.Field24 = None
        self.Field26 = None
        super().__init__()

class FbnBlock10Entry(Structure):
    _fields = [
        Field("Field00", S32, count=1, offset=None, endian=None),
        Field("Field04", S32, count=1, offset=None, endian=None),
        Field("Field08", F32, count=24, offset=None, endian=None),
        Field("Field68", S32, count=1, offset=None, endian=None),
        Field("Field6C", S32, count=1, offset=None, endian=None),
        Field("Field70", S32, count=1, offset=None, endian=None),
        Field("Field74", S32, count=1, offset=None, endian=None),
        Field("Field78", S16, count=1, offset=None, endian=None),
        Field("Field7A", S16, count=1, offset=None, endian=None),
        Field("Field7C", F32, count=6, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Field04 = None
        self.Field08 = None
        self.Field68 = None
        self.Field6C = None
        self.Field70 = None
        self.Field74 = None
        self.Field78 = None
        self.Field7A = None
        self.Field7C = None
        super().__init__()

class FbnBlock11SubEntry(Structure):
    _fields = [
        Field("Field00", IntFloat, count=1, offset=None, endian=None),
        Field("Field04", IntFloat, count=1, offset=None, endian=None),
        Field("Field08", IntFloat, count=1, offset=None, endian=None),
        Field("Field0C", IntFloat, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Field04 = None
        self.Field08 = None
        self.Field0C = None
        super().__init__()

class FbnBlock11Entry(Structure):
    _fields = [
        Field("Field00", S32, count=1, offset=None, endian=None),
        Field("Field04", F32, count=1, offset=None, endian=None),
        Field("Field08", S32, count=1, offset=None, endian=None),
        Field("Field0C", S32, count=1, offset=None, endian=None),
        Field("Field10", S32, count=1, offset=None, endian=None),
        Field("Field14", S32, count=1, offset=None, endian=None),
        Field("EntryCount", S16, count=1, offset=None, endian=None),
        Field("Field1A", S16, count=1, offset=None, endian=None),
        Field("Entries", FbnBlock11SubEntry, count="EntryCount", offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Field04 = None
        self.Field08 = None
        self.Field0C = None
        self.Field10 = None
        self.Field14 = None
        self.EntryCount = None
        self.Field1A = None
        self.Entries = None
        super().__init__()

class FbnNpc(Structure):
    _fields = [
        Field("Field00", S32, count=1, offset=None, endian=None),
        Field("Field04", Vector3, count=1, offset=None, endian=None),
        Field("Field10", Vector3, count=1, offset=None, endian=None),
        Field("Id", S16, count=1, offset=None, endian=None),
        Field("Field1E", S16, count=1, offset=None, endian=None),
        Field("Field20", S32, count=1, offset=None, endian=None),
        Field("Field24", S32, count=1, offset=None, endian=None),
        Field("Field28", S32, count=1, offset=None, endian=None),
        Field("PathNodeCount", S16, count=1, offset=None, endian=None),
        Field("Field2E", S16, count=1, offset=None, endian=None),
        Field("PathNodes", Vector3, count="PathNodeCount", offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Field04 = None
        self.Field10 = None
        self.Id = None
        self.Field1E = None
        self.Field20 = None
        self.Field24 = None
        self.Field28 = None
        self.PathNodeCount = None
        self.Field2E = None
        self.PathNodes = None
        super().__init__()

class FbnBlock18Entry(Structure):
    _fields = [
        Field("Field00", S32, count=1, offset=None, endian=None),
        Field("Field04", S16, count=1, offset=None, endian=None),
        Field("Field06", S16, count=1, offset=None, endian=None),
        Field("Position", Vector3, count=1, offset=None, endian=None),
        Field("Rotation", Quaternion, count=1, offset=None, endian=None),
        Field("Field24", S16, count=1, offset=None, endian=None),
        Field("Field26", S16, count=1, offset=None, endian=None),
        Field("Field28", S16, count=1, offset=None, endian=None),
        Field("Field2A", S16, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Field04 = None
        self.Field06 = None
        self.Position = None
        self.Rotation = None
        self.Field24 = None
        self.Field26 = None
        self.Field28 = None
        self.Field2A = None
        super().__init__()

class FbnBlock21Entry(Structure):
    _fields = [
        Field("Field00", S32, count=1, offset=None, endian=None),
        Field("Position", Vector3, count=1, offset=None, endian=None),
        Field("Rotation", Quaternion, count=1, offset=None, endian=None),
        Field("Field20", S16, count=1, offset=None, endian=None),
        Field("Field22", S16, count=1, offset=None, endian=None),
        Field("Field24", S16, count=1, offset=None, endian=None),
        Field("Field26", S16, count=1, offset=None, endian=None),
        Field("Field28", S16, count=1, offset=None, endian=None),
        Field("Field2A", S16, count=1, offset=None, endian=None),
        Field("Field2C", S32, count=1, offset=None, endian=None),
        Field("Field30", F32, count=1, offset=None, endian=None),
        Field("Field34", F32, count=1, offset=None, endian=None),
    ]
    def __init__( self ):
        self.Field00 = None
        self.Position = None
        self.Rotation = None
        self.Field20 = None
        self.Field22 = None
        self.Field24 = None
        self.Field26 = None
        self.Field28 = None
        self.Field2A = None
        self.Field2C = None
        self.Field30 = None
        self.Field34 = None
        super().__init__()

