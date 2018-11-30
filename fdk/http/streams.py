# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from fdk.http import parser


class ContentLengthStream(object):

    def __init__(self, base_stream, length):
        """
        Request body content stream
        :param base_stream: byte stream
        :param length: content length from request headers
        """
        self.base_stream = base_stream
        self.length = length
        self.bytes_read = 0
        self.closed = False

    async def close(self):
        """
        Close the file.
        A closed file cannot be used for further I/O operations.
        close() may be called more than once without error.
        """
        if not self.closed:
            while self.bytes_read < self.length:
                await self.read(self.length - self.bytes_read)
            self.closed = True

    async def read(self, size=-1):
        """
        Read at most size bytes, returned as bytes.
        Only makes one system call, so less
         data may be returned than requested.
        In non-blocking mode, returns None if no data is available.
        Return an empty bytes object at EOF.
        """
        if self.closed:
            raise OSError("Operation on closed stream")
        if size == -1 or size > (self.length - self.bytes_read):
            size = self.length - self.bytes_read
        val = await self.base_stream.read(size)
        if val is None:
            return None
        self.bytes_read += len(val)
        return val

    def readable(self):
        """
        True if file was opened in a read mode.
        """
        return True

    async def readall(self, *args, **kwargs):
        """
        Read all data from the file, returned as bytes.
        In non-blocking mode, returns as much as is immediately available,
        or None if no data is available.  Return an empty bytes object at EOF.
        """
        if self.closed:
            raise OSError("Operation on closed stream")
        val = bytes()
        while self.bytes_read < self.length:
            more = await self.read()
            if more == b'':
                break
            val += more
        return val

    def seek(self):
        """
        Move to new file position and return the file position.
        Argument offset is a byte count.  Optional argument whence defaults to
        SEEK_SET or 0 (offset from start of file, offset should be >= 0);
        other values are SEEK_CUR or 1 (move relative to current position,
         positive or negative),
        and SEEK_END or 2 (move relative to end of file,
         usually negative, although
        many platforms allow seeking beyond the end of a file).
        Note that not all file objects are seekable.
        """
        raise OSError()

    def seekable(self):
        """ True if file supports random-access. """
        return False

    def tell(self):
        """
        Current file position.
        Can raise OSError for non seekable files.
        """
        raise OSError()

    def truncate(self):
        """
        Truncate the file to at most size bytes and return
         the truncated size.
        Size defaults to the current file position, as returned by tell().
        The current file position is changed to the value of size.
        """
        raise OSError()

    def writable(self):
        """ True if file was opened in a write mode. """
        return False

    def write(self):
        """
        Write buffer b to file, return number of bytes written.
        Only makes one system call, so not all of the data may be written.
        The number of bytes actually written is returned.
          In non-blocking mode,
        returns None if the write would block.
        """
        raise OSError()

    def __repr__(self):
        """ Return repr(self). """
        return "ContentLengthStream({}/{})".format(
            self.bytes_read, self.length)

    @property
    def closefd(self):
        """True if the file descriptor will be closed by close()."""
        return False

    @property
    def mode(self):
        """String giving the file mode"""
        return "rb"


class ChunkedStream(object):
    """Read from a chunked stream
    Data is sent in a series of chunks. The Content-Length header
    is omitted in this case and at the beginning of
    each chunk you need to add the length of the current chunk in
    hexadecimal format, followed by '\r\n' and then
    the chunk itself, followed by another '\r\n'. The terminating
    chunk is a regular chunk, with the exception that
    its length is zero.
    """
    def __init__(self, base_stream):
        """
        Chunked stream reader
        :param base_stream: byte stream
        """
        self.base_stream = base_stream
        self.closed = False
        self.eof = False
        self.current_chunk = bytes()
        self.current_length = -1  # Signal we need a new block
        self.current_read = 0

    async def close(self):
        """
        Close the file.
        A closed file cannot be used for further I/O operations.
          close() may be
        called more than once without error.
        In our case, we continue reading until we are closed.
        """
        if not self.closed:
            while not self.eof:
                await self.read()
            self.closed = True

    async def read(self, size=-1):
        """
        Read at most size bytes, returned as bytes.
        Only makes one system call, so less data may be
         returned than requested.
        In non-blocking mode, returns None if no data
         is available.
        Return an empty bytes object at EOF.
        """
        if self.closed:
            raise OSError("Operation on closed stream")

        while True:
            if self.eof:
                return bytes()

            # Do we need to read a new chunk?
            if self.current_length == -1:
                # Yes: read a line up to \r\n with the hex
                #  length of the chunk in it
                line = await parser.readline(self.base_stream)
                line = line.rstrip()
                self.current_read = 0
                self.current_length = int(line, 16)
                self.current_chunk = bytes()

            # Do we need more of this chunk?
            if self.current_read < self.current_length:
                if size < 0 or size > (self.current_length -
                                       self.current_read):
                    size = self.current_length - self.current_read
                if len(self.current_chunk) < self.current_length:
                    # Read more in
                    more = await self.base_stream.read(size)
                    if more is None:
                        return None
                    self.current_chunk += more
                from_size = self.current_read + size
                result = (
                    self.current_chunk[self.current_read:from_size])
                self.current_read += len(result)
                return result

            # Otherwise, read in the \r\n
            if (await self.base_stream.read(1) != b'\r' or
                    await self.base_stream.read(1) != b'\n'):
                raise OSError("malformed chunk")

            if self.current_length == 0:
                self.eof = True

            self.current_length = -1

    def readable(self):
        """ True if file was opened in a read mode. """
        return True

    async def readall(self, *args, **kwargs):
        """
        Read all data from the file, returned as bytes.
        In non-blocking mode, returns as much as is
         immediately available,
        or None if no data is available.  Return an empty
         bytes object at EOF.
        """
        if self.closed:
            raise OSError("Operation on closed stream")
        val = bytes()
        while True:
            more = await self.read()
            if more is None or len(more) == 0:
                return val
            val += more

    def seek(self):
        """
        Move to new file position and return the file position.
        Argument offset is a byte count.
        Optional argument whence defaults to
        SEEK_SET or 0 (offset from start of file, offset
        should be >= 0); other values
        are SEEK_CUR or 1 (move relative to current position,
        positive or negative),
        and SEEK_END or 2 (move relative to end of file, usually
        negative, although
        many platforms allow seeking beyond the end of a file).
        Note that not all file objects are seekable.
        """
        raise OSError()

    def seekable(self):
        """ True if file supports random-access. """
        return False

    def tell(self):
        """
        Current file position.
        Can raise OSError for non seekable files.
        """
        raise OSError()

    def truncate(self):
        """
        Truncate the file to at most size bytes and
         return the truncated size.
        Size defaults to the current file position,
         as returned by tell().
        The current file position is changed to the value of size.
        """
        raise OSError()

    def writable(self):
        """
        True if file was opened in a write mode
        """
        return False

    def write(self):
        """
        Write buffer b to file, return number of bytes written.
        Only makes one system call, so not all of the data may be written.
        The number of bytes actually written is returned.
         In non-blocking mode,
        returns None if the write would block.
        """
        raise OSError()

    @property
    def closefd(self):
        """
        True if the file descriptor will be closed by close()
        """
        return False

    @property
    def mode(self):
        """
        String giving the file mode
        """
        return "rb"
