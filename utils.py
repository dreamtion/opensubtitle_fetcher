import os
import struct


def hashfile(name):
    """This is the copy of example hashing function:
    http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
    """
    try:
        longlongformat = '<q'  # little-endian long long
        bytesize = struct.calcsize(longlongformat)
        f = open(name, "rb")
        filesize = os.path.getsize(name)
        hash = filesize
        if filesize < 65536 * 2:
            return "SizeError"
        for x in range(65536/bytesize):
            buffer = f.read(bytesize)
            (l_value,) = struct.unpack(longlongformat, buffer)
            hash += l_value
            # to remain as 64bit number
            hash = hash & 0xFFFFFFFFFFFFFFFF
        f.seek(max(0, filesize-65536), 0)
        for x in range(65536/bytesize):
            buffer = f.read(bytesize)
            (l_value,) = struct.unpack(longlongformat, buffer)
            hash += l_value
            hash = hash & 0xFFFFFFFFFFFFFFFF
        f.close()
        returnedhash = "%016x" % hash
        return returnedhash, filesize
    except(IOError):
        return "IOError"


def unzip(filename, output_dir, delete=True):
    """Re-implement of command 'unzip -d FILENAME'
    """
    import gzip

    if not filename.endswith('.gz'):
        print "Probably not a gz file?"
        return
    in_file = os.path.basename(filename)
    out_file = os.path.join(output_dir, in_file.strip('.gz'))

    in_f = gzip.GzipFile(filename, 'rb')
    f_content = in_f.read()
    in_f.close()

    if delete:
        os.remove(filename)

    with open(out_file, 'wb') as out_f:
        out_f.write(f_content)
    return out_file
