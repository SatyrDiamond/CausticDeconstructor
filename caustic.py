
from functions import data_bytes
import struct

global caustic_instnames
caustic_instnames = {}
caustic_instnames['NULL'] = 'None'
caustic_instnames['SSYN'] = 'SubSynth'
caustic_instnames['PCMS'] = 'PCMSynth'
caustic_instnames['BLNE'] = 'BassLine'
caustic_instnames['BBOX'] = 'BeatBox'
caustic_instnames['PADS'] = 'PadSynth'
caustic_instnames['8SYN'] = '8BitSynth'
caustic_instnames['MDLR'] = 'Modular'
caustic_instnames['ORGN'] = 'Organ'
caustic_instnames['VCDR'] = 'Vocoder'
caustic_instnames['FMSN'] = 'FMSynth'
caustic_instnames['KSSN'] = 'KSSynth'
caustic_instnames['SAWS'] = 'SawSynth'

patletters = ['A','B','C','D']

#python caustic_test.py

global EFFX_num
    
EFFX_num = 1


def parse_note(SPAT_str, numnotes):
    notelist = []
    for _ in range(numnotes): 
        notedata = struct.unpack("IIffffIIIfffff", SPAT_str.read(56))
        #print(notedata)
        notelist.append(notedata)
    return notelist

def deconstruct_SPAT(bio_in):
    global patletters

    print('[format-caustic] SPAT |')
    if bio_in.read(4) != b'SPAT':
        print('data is not SPAT')
        exit()

    l_patterns = {}

    for patletter in range(4): 
        for patnum in range(16): 
            l_patterns[patletters[patletter]+str(patnum+1)] = {}

    SPAT_size = int.from_bytes(bio_in.read(4), "little")
    SPAT_data = bio_in.read(SPAT_size)
    SPAT_str = data_bytes.bytearray2BytesIO(SPAT_data)

    # --------------- measures ---------------
    for patletter in range(4): 
        for patnum in range(16): 
            l_patterns[patletters[patletter]+str(patnum+1)]['measures'] = int.from_bytes(SPAT_str.read(4), "little")

    # --------------- numnote ---------------
    for patletter in range(4): 
        for patnum in range(16): 
            l_patterns[patletters[patletter]+str(patnum+1)]['numnote'] = int.from_bytes(SPAT_str.read(4), "little")

    # --------------- notes data ---------------
    for patletter in range(4): 
        for patnum in range(16): 
            numnote = l_patterns[patletters[patletter]+str(patnum+1)]['numnote']
            parse_note(SPAT_str, numnote)

def deconstruct_CCOL(bio_in):
    print('[format-caustic] CCOL |', end=' ')
    if bio_in.read(4) != b'CCOL':
        print('data is not CCOL')
        exit()
    CCOL_size = int.from_bytes(bio_in.read(4), "little")
    CCOL_data = bio_in.read(CCOL_size)
    CCOL_chunks = data_bytes.riff_read(CCOL_data, 0)
    CCOL_l_out = {}
    for part in CCOL_chunks:
        con_id = int.from_bytes(part[1][:4], "little")
        con_value = struct.unpack('<f', part[1][4:])[0]
        CCOL_l_out[con_id] = con_value
    print(str(len(CCOL_l_out))+' Controls')
    return CCOL_l_out

def deconstruct_EFFX(bi_rack, Caustic_Main):
    print('[format-caustic] EFFX')
    global EFFX_num
    EFFX_size = int.from_bytes(bi_rack.read(4), "little")
    EFFX_data = bi_rack.read(EFFX_size)
    if EFFX_num == 1: bi_rack.read(4)
    Caustic_Main['EFFX'+str(EFFX_num)] = EFFX_data
    EFFX_num += 1

def deconstruct_machine(datain, l_machine):
    #print(datain[:100])
    data_str = data_bytes.bytearray2BytesIO(datain)
    if l_machine['id'] == 'SSYN': # SubSynth
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        l_machine['unknown4'] = int.from_bytes(data_str.read(4), "little")
        l_machine['customwaveform1'] = data_str.read(1320)
        l_machine['customwaveform2'] = data_str.read(1320)
        data_str.read(12)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    elif l_machine['id'] == 'BLNE': # BassLine
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
        data_str.read(4)
        l_machine['customwaveform'] = data_str.read(1320)
    elif l_machine['id'] == 'PADS': # PadSynth
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['unknown1'] = int.from_bytes(data_str.read(4), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(4), "little")
        l_machine['harm1'] = struct.unpack("ffffffffffffffffffffffff", data_str.read(96))
        l_machine['harm1vol'] = struct.unpack("f", data_str.read(4))[0]
        l_machine['harm2'] = struct.unpack("ffffffffffffffffffffffff", data_str.read(96))
        l_machine['harm2vol'] = struct.unpack("f", data_str.read(4))[0]
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    elif l_machine['id'] == 'ORGN': # Organ
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['unknown1'] = int.from_bytes(data_str.read(4), "little")
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    elif l_machine['id'] == 'FMSN': # FMSynth
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['unknown4'] = int.from_bytes(data_str.read(4), "little")
        l_machine['unknown5'] = int.from_bytes(data_str.read(4), "little")
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
        print(data_str.read(100))
    else: exit()


def deconstruct_OUTP(bi_rack, Caustic_Main):
    global caustic_machdata
    OUTP_size = int.from_bytes(bi_rack.read(4), "little")
    OUTP_data = bi_rack.read(OUTP_size)

    caustic_machines = []

    for _ in range(14):
        machtype = bi_rack.read(4).decode("utf-8")
        bi_rack.read(1)
        caustic_machines.append({'id': machtype})

    te_num = 0
    for machpart in caustic_machines:
        print('[format-caustic] OUTP |', end=' ')
        print(caustic_instnames[machpart['id']], end='')
        if machpart['id'] != 'NULL':
            bi_rack.read(10)
            te_name = bi_rack.read(4)
            te_size = int.from_bytes(bi_rack.read(4), "little")
            print(', '+str(te_size))
            te_data = bi_rack.read(te_size)
            caustic_machines[te_num]['data'] = te_data
            deconstruct_machine(te_data, caustic_machines[te_num])
            #print(te_data[:100])
        else: print()
        te_num += 1
    Caustic_Main['Machines'] = caustic_machines


def deconstruct_main(filepath):
    fileobject = open(filepath, 'rb')
    headername = fileobject.read(4)
    ro_rack = data_bytes.riff_read(fileobject, 0)

    for rod_rack in ro_rack:
        if rod_rack[0] == b'RACK':
            rackdata = rod_rack[1]
            bi_rack = data_bytes.bytearray2BytesIO(rackdata)

    bi_rack.seek(0,2)
    racksize = bi_rack.tell()
    bi_rack.seek(0)

    header = bi_rack.read(264)

    Caustic_Main = {}

    while racksize > bi_rack.tell():
        chunk_datatype = bi_rack.read(4)
        print('[format-caustic] main | chunk:', chunk_datatype)
        if chunk_datatype == b'OUTP': deconstruct_OUTP(bi_rack, Caustic_Main)
        elif chunk_datatype == b'EFFX': deconstruct_EFFX(bi_rack, Caustic_Main)
        else: break

    return Caustic_Main














CausticData = deconstruct_main('G:\\RandomMusicFiles\\caustic\\documents\\songs\\Test.caustic')

#machinedata = CausticData['Machines'][0]
