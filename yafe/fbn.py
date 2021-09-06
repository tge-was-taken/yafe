import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/../'))
from yafe.io import Endian, BinaryStream, Structure, Field, U32
from yafe.structs.fbn import *

class FbnListHeader(Structure):
    _fields = [
        Field('EntryCount', U32),
        Field('Padding', U32, count=3),
    ]
            
class FbnList:
    def __init__( self ) -> None:
        self.block = None
        self.header = None
        self.items = []
    
class FbnBinary:
    BLOCK_MAP = {
        1: FbnTriggerVolume,
        4: FbnEntrance,
        5: FbnHitDefinition,
        8: FbnBlock8Entry,
        9: FbnBlock9Entry,
        10: FbnBlock10Entry,
        11: FbnBlock11Entry,
        14: FbnNpc,
        18: FbnBlock18Entry,
        19: FbnTriggerVolume,
        21: FbnBlock21Entry,
        22: FbnTriggerVolume
    }

    def __init__(self) -> None:
        self.blocks = []
        
    def getBlockByType( self, type ):
        for block in self.blocks:
            if block[0].Type == type:
                return block
        return None
    
    def _readImpl( self, stream: BinaryStream ) -> None:
        while not stream.checkEOF():
            blockStart = stream.getOffset()
            block = FbnBlock.read( stream )
            entries = None
            if block.ListOffset != 0:
                entryType = None
                if block.Type in self.BLOCK_MAP:
                    entryType = self.BLOCK_MAP[block.Type]
                else:
                    raise NotImplementedError(f"Unimplemented block type: {block.Type}")
                
                listHeader = FbnListHeader.read( stream )
                for i in range( 0, len( listHeader.Padding ) ):
                    if listHeader.Padding[i] != 0:
                        raise Exception( "Padding values in list header not zero" )
                
                entries = []
                for i in range( 0, listHeader.EntryCount ):
                    entries.append( entryType.read( stream ) )     
            self.blocks.append( ( block, entries ) )
            stream.setOffset( blockStart + block.Size )
            
    def _writeImpl( self, stream: BinaryStream ) -> None:
        for block, entries in self.blocks:
            # write initial block data
            blockStartOff = stream.getOffset()
            block.write( stream )
            if entries != None:
                # write list header
                block.ListOffset = stream.getOffset() - blockStartOff
                listHeader = FbnListHeader()
                listHeader.EntryCount = len( entries )
                listHeader.write( stream )
               
                # write list data
                for entry in entries:
                    entry.write( stream )
            else:
                block.ListOffset = 0
                    
            # calc size
            blockEndOff = stream.getOffset()
            blockSize = blockEndOff - blockStartOff
            
            # rewrite block header
            block.Size = blockSize
            stream.setOffset( blockStartOff )
            block.write( stream )
            stream.setOffset( blockEndOff )
            
    @classmethod
    def read( cls, stream ):
        inst = cls()
        cls._readImpl( inst, stream )
        return inst
    
    def write( self, stream ):
        self._writeImpl( stream )
    
# def test():
#     with BinaryStream.openReadFile( "X:/dumps/p5_ps3_eu/ps3/ps3.cpk_unpacked/field/f001_001.pac_extracted/data/f001_001_00.FBN", Endian.BIG ) as stream:
#         fbn = FbnBinary.read( stream )

#         with BinaryStream( None, Endian.BIG ) as outStream:
#             fbn.write( outStream )
#             with open( 'test.fbn', "wb" ) as f:
#                 f.write(outStream.getBuffer())
#         pass
    
#     with BinaryStream.openReadFile( "X:/dumps/p5_ps3_eu/ps3/ps3.cpk_unpacked/field/f001_001.pac_extracted/hit/f001_001_00.HTB", Endian.BIG ) as stream:
#         htb = FbnBinary.read( stream )

#         with BinaryStream( None, Endian.BIG ) as outStream:
#             htb.write( outStream )
#             with open( 'test.htb', "wb" ) as f:
#                 f.write(outStream.getBuffer())
#         pass
    
# if __name__ == '__main__':
#     test()
    