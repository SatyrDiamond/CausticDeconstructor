
from functions import data_bytes

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
        print('[input-caustic] outp |', end=' ')
        print('type:', machpart['id'], end=' | ')
        if machpart['id'] != 'NULL':
            bi_rack.read(10)
            te_name = bi_rack.read(4)
            te_size = int.from_bytes(bi_rack.read(4), "little")
            print('size: '+str(te_size))
            te_data = bi_rack.read(te_size)
            caustic_machines[te_num][1] = te_data
        else:
            print()
        te_num += 1
    return caustic_machines


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
        print('[input-caustic] main | chunk:', chunk_datatype)
        if chunk_datatype == b'OUTP': deconstruct_OUTP(bi_rack, Caustic_Main)
        else: break

deconstruct_main('G:\\RandomMusicFiles\\caustic\\documents\\songs\\Test.caustic')
