import sys
import itertools
from BitVector import *                                                       #(A)

if len(sys.argv) is not 3:                                                    #(B)
    sys.exit('''Needs two command-line arguments, one for '''
             '''the message file and the other for the '''
             '''encrypted output file''')

PassPhrase = "Hopes and dreams of a million years"                            #(C)

BLOCKSIZE = 16                                                                #(D)
numbytes = BLOCKSIZE // 8                                                     #(E)

# Reduce the passphrase to a bit array of size BLOCKSIZE:
bv_iv = BitVector(bitlist = [0]*BLOCKSIZE)                                    #(F)
for i in range(0,len(PassPhrase) // numbytes):                                #(G)
    textstr = PassPhrase[i*numbytes:(i+1)*numbytes]                           #(H)
    bv_iv ^= BitVector( textstring = textstr )                                #(I)

# Reduce the key to a bit array of size BLOCKSIZE:
keys = []                            #(P)
for x in map(''.join, itertools.product('01', repeat=BLOCKSIZE)):
    keys.append(BitVector(bitstring = x))              
    

count = 0
for key_bv in keys:                                                         #(Q)
    msg_encrypted_bv = BitVector( size = 0 )                                      #(R)
    previous_block = bv_iv                                                        #(S)
    bv = BitVector( filename = sys.argv[1] )                                      #(T)
    while (bv.more_to_read):                                                      #(U)
        bv_read = bv.read_bits_from_file(BLOCKSIZE)                               #(V)
        if len(bv_read) < BLOCKSIZE:                                              #(W)
            bv_read += BitVector(size = (BLOCKSIZE - len(bv_read)))               #(X)
        bv_read ^= key_bv                                                         #(Y)
        bv_read ^= previous_block                                                 #(Z)
        previous_block = bv_read.deep_copy()                                      #(a)
        msg_encrypted_bv += bv_read                                               #(b)

    # Convert the encrypted bitvector into a hex string:    
    outputhex = msg_encrypted_bv.get_hex_string_from_bitvector()                  #(c)

    if (outputhex.find("20352a7e36703a6930767f7276397e376528632d6b6665656f6f6424623c2d30272f3c2d3d2172396933742c7e233f687d2e32083c11385a03460d440c25") != -1):
        FILEOUT = open(f'{count}-{sys.argv[2]}', 'w')                                              #(d)
        FILEOUT.write(outputhex)                                                      #(e)
        FILEOUT.close()  
    count += 1
