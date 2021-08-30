from io import SEEK_END, SEEK_SET, IOBase
from os import stat
import struct
from typing import Any, Type
import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/../../'))

class Endian:
    LITTLE = 0
    BIG = 1
    STRUCT_FORMAT = ['<', '>']

class BinaryStream:
    def __init__( self, buffer = None, endian = Endian.LITTLE ):
        self.bufferOffset = 0
        self.bufferStartOffset = 0
        self.offset = 0
        self.capacity = 4
        self.setEndian( endian )
        
        if isinstance( buffer, IOBase ):
            # passed a file stream instead of memory buffer
            self.io = buffer
            self.buffer = None
            
            # determine file size
            self.io.seek( 0, SEEK_END )
            self.size = self.io.tell()
            self.io.seek( 0, SEEK_SET )   
           
            if self.size > 0:
                 # read read buffer
                self.buffer = self.io.read( min( self.size, self.capacity ) )
                self.capacity = len( self.buffer )
            else:
                # allocate write buffer
                self.buffer = bytearray( self.capacity )
        else:
            # passed a memory buffer
            self.io = None
            self.buffer = buffer

            if self.buffer != None:
                # use passed read buffer
                self.size = len( self.buffer )
                self.capacity = self.size
            else:
                # alloc write buffer
                self.buffer = bytearray( 1024 * 1024 )
                self.capacity = len( self.buffer )
                self.size = 0
            
    def __enter__( self ):
        return self
    
    def __exit__( self, type, value, tb ):
        pass
    
    def _flush( self ):
        if self.io != None:
            # flush to file
            self.io.write( self.buffer )
            self.bufferOffset = 0
            self.bufferStartOffset = self.offset
        
    def _checkCapacity( self, size ):
        return self.bufferOffset + size <= self.capacity
    
    def _ensureWriteCapacity( self, size ):
        while self.bufferOffset + size > self.capacity:
            oldCapacity = self.capacity
            self.capacity *= 2
            self.buffer.extend([0] * ( self.capacity - oldCapacity ) )
            
    def _ensureReadCapacity( self, size ):
        while self.bufferOffset + size > self.capacity:
            oldCapacity = self.capacity
            self.capacity *= 2
            
            self.io.seek( self.offset )
            self.buffer = self.io.read( min( self.size - self.offset, self.capacity ) )
            self.capacity = len( self.buffer )
            self.bufferOffset = 0
            self.bufferStartOffset = self.offset
        
    def _writeArray( self, size, fmt, *data ):
        if self.io != None and not self._checkCapacity( size ):
            self._flush()
            
        self._ensureWriteCapacity( size )
        struct.pack_into( self.endianFmt + fmt, self.buffer, self.bufferOffset, *data )
        self.offset += size
        self.bufferOffset += size
        self.size = max( self.size, self.offset )
        
    def _write( self, size, fmt, data ):
        if self.io != None and not self._checkCapacity( size ):
            self._flush()
        
        self._ensureWriteCapacity( size )
        struct.pack_into( self.endianFmt + fmt, self.buffer, self.bufferOffset, data )
        self.offset += size
        self.bufferOffset += size
        self.size = max( self.size, self.offset )
        
    def _read( self, size, fmt ):
        if self.io != None and not self._checkCapacity( size ):
            self._ensureReadCapacity( size )
        
        data = struct.unpack_from( self.endianFmt + fmt, self.buffer, self.bufferOffset )
        self.offset += size
        self.bufferOffset += size
        return data
            
    def getBuffer( self ):
        if self.capacity > self.size:
            return self.buffer[0:self.size]
        else:
            return self.buffer
    
    def getSize( self ):
        return self.size
    
    def getOffset( self ):
        return self.offset
    
    def setOffset( self, offset ):
        self.offset = offset
        self.bufferOffset = offset
    
    def setEndian( self, endian ):
        self.endian = endian
        self.endianFmt = Endian.STRUCT_FORMAT[ self.endian ]
        
    def checkEOF( self ):
        return self.getOffset() >= self.getSize()
    
    def writeBytes( self, data ):
        self._writeArray( len(data), "B" * len(data), *data )
            
    def writeByte( self, data ):
        self._ensureWriteCapacity( 1 )
        self.buffer[ self.bufferOffset ] = data & 0xFF
        self.bufferOffset += 1
        self.offset += 1
        
    def writeBool( self, data ):
        self.writeByte( data )
        
    def writeUByte( self, data ):
        self.writeByte( data )
        
    def writeShort( self, data ):
        self._write( 2, "h", data )
        
    def writeUShort( self, data ):
        self._write( 2, "H", data & 0xFFFF )
        
    def writeInt( self, data ):
        self._write( 4, "i", data )
        
    def writeUInt( self, data ):
        self._write( 4, "I", data & 0xFFFFFFFF  )
        
    def writeInt64( self, data ):
        self._write( 8, "q", data )
        
    def writeUInt64( self, data ):
        self._write( 8, "Q", data & 0xFFFFFFFFFFFFFFFF )
        
    def writeFloat( self, data ):
        self._write( 4, "f", data )
        
    def writeDouble( self, data ):
        self._write( 8, "d", data )
        
    def readBytes( self, count ):
        return bytes( self._read( count, "B" * count ) )
        
    def readBool( self ):
        return self._read( 1, "B" )[0] != 0
    
    def readByte( self ):
        return self._read( 1, "b" )[0]
    
    def readUByte( self ):
        return self._read( 1, "B" )[0]
    
    def readShort( self ):
        return self._read( 2, "h" )[0]
    
    def readUShort( self ):
        return self._read( 2, "H" )[0]
    
    def readInt( self ):
        return self._read( 4, "i" )[0]
    
    def readUInt( self ):
        return self._read( 4, "I" )[0]
    
    def readFloat( self ):
        return self._read( 4, "f" )[0]
    
    def readDouble( self ):
        return self._read( 4, "d" )[0]
    
    def readInt64( self ):
        return self._read( 8, "q" )[0]
    
    def readUInt64( self ):
        return self._read( 8, "Q" )[0]
    
    def readString( self ):
        buffer = bytearray()
        b = self.readByte()
        s = ""
        while b != 0:
            buffer.append( b )
            b = self.readByte()
            
        return buffer.decode( "ascii" )
    
    @staticmethod
    def openReadFile( path, endian = Endian.LITTLE ):
        #return BinaryStream( open( path, "rb" ), endian )
        with open( path, "rb" ) as f:
            return BinaryStream( f.read(), endian )
        
class Field:
    def __init__( self, name: str, type: Type, count=1, offset=None, **kwargs: dict ):
        self.name = name
        self.type = type
        self.count = count
        self.offset = offset
        for key,val in kwargs:
            setattr(self, key, val)
            
    def __repr__(self) -> str:
        return (self.name, self.type, self.count, self.offset).__repr__()
            
    def isArray( self ):
        return isinstance( self.count, str ) or self.count > 1
    
    def isFixedArray( self ):
        return isinstance( self.count, int )
    
    def getFixedArrayCount( self ):
        if isinstance( self.count, int ):
            return self.count
        else:
            return None
            
    def resolveFieldCount( self, obj: Any ):
        if isinstance( self.count, str ):
            if hasattr( obj, self.count ):
                return getattr( obj, self.count )
            else:
                return None
        else:
            return self.count
        
    def resolveFieldOffset( self, stream: BinaryStream, baseOffset ):
        if self.offset != None:
            return self.offset
        else:
            return stream.getOffset() - baseOffset
    
    def getDefaultValue( self ):
        defaultValue = self.type()
        if hasattr( self.type, '_DEFAULT_VALUE' ):
            defaultValue = self.type._DEFAULT_VALUE
        return defaultValue
    
    def getUnderlyingType( self ):
        utype = self.type
        if hasattr( self.type, '_UNDERLYING_TYPE' ):
            utype = self.type._UNDERLYING_TYPE
        return utype

class _BasicType:
    _DEFAULT_VALUE = int()
    _UNDERLYING_TYPE = int
    
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ): raise NotImplementedError
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: raise NotImplementedError

class S8(_BasicType):
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> int: return stream.readByte()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: stream.writeByte( value )
    
class U8(_BasicType):
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> int: return stream.readUByte()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: stream.writeUByte( value )

class S16(_BasicType):
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> int: return stream.readShort()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: stream.writeShort( value )
        
class U16(_BasicType):
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> int: return stream.readUShort()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: stream.writeUShort( value )
        
class S32(_BasicType):
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> int: return stream.readInt()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: stream.writeInt( value )
        
class U32(_BasicType):
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> int: return stream.readUInt()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: stream.writeUInt( value )
        
class S64(_BasicType):
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> int: return stream.readInt64()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: stream.writeInt64( value )
        
class U64(_BasicType):
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> int: return stream.readUInt64()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: int ) -> None: stream.writeUInt64( value )
        
class F32(_BasicType):
    _DEFAULT_VALUE = float()
    _UNDERLYING_TYPE = float
    
    @staticmethod
    def _read( parent: Any, field: Field, stream: BinaryStream ) -> float: return stream.readFloat()
    
    @staticmethod
    def _write( parent: Any, field: Field, stream: BinaryStream, value: float ) -> None: stream.writeFloat( value )
        
class Structure(object):
    def __init__( self ):
        # init attributes
        for field in self._fields:
            if field.isArray():
                count = field.getFixedArrayCount()
                value = []
                if count != None:
                    # fill array of its a fixed array
                    for i in range( 0, count ):
                        value.append( field.getDefaultValue() )    
                setattr( self, field.name, value )
            else:   
                setattr( self, field.name, field.getDefaultValue() )
                
    def __repr__(self) -> str:
        values = ", ".join(f"{name}={value}"
                          for name, value in self._asdict().items())
        return f"<{self.__class__.__name__}: {values}>"

    def _asdict(self) -> dict:
        return {field.name: getattr(self, field.name)
                for field in self._fields}
            
    def _readImpl( self, stream: BinaryStream ) -> object:
        # read fields
        baseOffset = stream.getOffset()
        for field in self._fields:
            name = field.name
            type = field.type
            count = field.resolveFieldCount( self )
            offset = field.resolveFieldOffset( stream, baseOffset )
            
            stream.setOffset( baseOffset + offset )
            if field.isArray():
                # read array
                elems = []
                for i in range( 0, count ):
                    elems.append( type._read( self, field, stream ) )
                setattr( self, name, elems )
            else:
                # read single value
                setattr( self, name, type._read( self, field, stream ) )
                
    def _writeImpl( self, stream: BinaryStream ) -> None:
        # write fields
        baseOffset = stream.getOffset()
        for field in self._fields:
            name = field.name
            type = field.type
            count = field.resolveFieldCount( self )
            offset = field.resolveFieldOffset( stream, baseOffset )
            
            stream.setOffset( baseOffset + offset )
            if field.isArray():
                # write array
                elems = getattr( self, name )
                for i in range( 0, count ):
                    type._write( self, field, stream, elems[i] )
            else:
                # write single value
                type._write( self, field, stream, getattr( self, name ) )
      
    # rewritten into read( stream ) so is compatible with required signature
    @classmethod          
    def _read( cls, parent, field, stream: BinaryStream ):
        inst = cls()
        inst._readImpl( stream )
        return inst
        
    # rewritten into read( stream ) so is compatible with required signature
    @classmethod          
    def read( cls, stream: BinaryStream ):
        return cls._read( None, None, stream )
    
    # rewritten into write( obj, stream ) so is compatible with required signature
    def _write( parent: Any, field: Field, stream: BinaryStream, value: Any ) -> None: 
        value._writeImpl( stream )
    
    def write( self, stream: BinaryStream ):
        self._writeImpl( stream )
                
def test():
    def iterObjectFields( obj, field, path ):
        if hasattr( obj, '_fields' ):
            for field in obj._fields:
                val = getattr( obj, field.name )
                fieldPath = path + "." + field.name if path != None else field.name
                
                if isinstance( val, Structure ):
                    # collapse struct
                    yield from iterObjectFields( val, field, fieldPath )
                elif isinstance( val, list ):
                    # skip variable arrays
                    if not field.isFixedArray():
                        continue
                        
                    # generate fixed array
                    for i, item in enumerate( val ):
                        yield from iterObjectFields( item, field, f"{fieldPath}[{i}]" )
                else:
                    yield from iterObjectFields( val, field, fieldPath )
        else:
            # terminal node
            print( path )
            yield obj, field, path
    
    from yafe.fbn import FbnBinary
    with BinaryStream.openReadFile( "X:/dumps/p5_ps3_eu/ps3/ps3.cpk_unpacked/field/f001_001.pac_extracted/data/f001_001_00.FBN", Endian.BIG ) as stream:
        fbn = FbnBinary.read( stream )
        for block, items in fbn.blocks:
            for val, field, path in iterObjectFields( block, None, None ):
                print( path )         
        

        
if __name__ == '__main__':
    test()