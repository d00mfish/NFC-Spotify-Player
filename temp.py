

'''
    #while(True):
    #   val = RFID_read()
    #    if val is None:
    #        continue
    #    else:
    #        print([hex(x) for x in val])
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None:
        retval = None
    else:
        print("Authenticating block 4 ...")
        authenticated = pn532.mifare_classic_authenticate_block(uid, 4, MIFARE_CMD_AUTH_B, key)
        if not authenticated:
            print("Authentication failed!")
            retval = -1
        else:
            uri = "spotify:user:d00mfish:playlist:5wl2CwPc6yXN0wsbnvrWBf".split(':')
            bytearray(16) = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            pn532.mifare_classic_write_block(4,)
    return retval
'''

uri = "spotify:user:d00mfish:playlist:5wl2CwPc6yXN0wsbnvrWBf"
parts = [uri[i:i+16] for i in range(0, len(uri), 16)]
print(parts)
#making bytearrays with 16bytes of size, no matter what
b1 = bytearray(parts[0],'utf-8')+bytearray(16-len(parts[0]))
b2 = bytearray(parts[1],'utf-8')+bytearray(16-len(parts[1]))
b3 = bytearray(parts[2],'utf-8')+bytearray(16-len(parts[2]))
b4 = bytearray(parts[3],'utf-8')+bytearray(16-len(parts[3]))
print(b4)
#for i in range(len(parts)):
    #pn532.mifare_classic_write_block(i+4,parts[i])

parts = (b1+b2+b3+b4).decode('utf-8').strip('\x00')
print(parts)
#parts.strip()

if -1 in (b1,b2,b3,b4):
    print("test")



