"""无 ffprobe 时，直接从 mp4 二进制读取时长 / 分辨率 / 音轨信息。

用法：python probe_mp4.py <path.mp4>
"""
import struct
import sys

path = sys.argv[1]
data = open(path, 'rb').read()

i = data.find(b'mvhd')
mv = data[i:]
ver = mv[4]
if ver == 0:
    ts, dur = struct.unpack('>II', mv[16:24])
else:
    ts, dur = struct.unpack('>IQ', mv[24:36])
print('duration_sec = %.2f' % (dur / float(ts)))

for tag in (b'tkhd',):
    pos = 0
    while True:
        j = data.find(tag, pos)
        if j < 0:
            break
        t = data[j:]
        w = struct.unpack('>I', t[80:84])[0] >> 16
        h = struct.unpack('>I', t[84:88])[0] >> 16
        print('track size = %dx%d' % (w, h))
        pos = j + 4

print('has_audio = %s' % (b'mp4a' in data or b'soun' in data[:200000]))
print('file_mb = %.2f' % (len(data) / 1024.0 / 1024.0))
