import sys


def read_msr(msr_number):
    try:
        with open('/dev/cpu/0/msr', 'rb') as f:
            f.seek(msr_number)
            data = f.read(8)
            return int.from_bytes(data, 'little')
    except Exception as e:
        print(e)

def read_bit(value, bit):
    return (value >> bit) & 0x1


msr_address = int(sys.argv[1])
msr_value = read_msr(msr_address)
if msr_value is not None:
    bit = int(sys.argv[2])
    bit_value = read_bit(msr_value, bit)
    print("Bit {0} value of msr {1} = {2}".format(bit, msr_address, bit_value))
