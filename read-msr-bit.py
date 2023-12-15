import sys

def read_msr(msr_number):
    try:
        with open('/dev/cpu/0/msr', 'rb') as f:
            f.seek(msr_number)
            return int.from_bytes(f.read(8), 'little')
    except FileNotFoundError:
        print("msr file not found")

def read_bit(value, bit):
    return (value >> bit) & 0x1


msr_address = int(sys.argv[1])
msr_value = read_msr(msr_address)
if msr_value is not None:
    bit = int(sys.argv[2])
    bit_value = read_bit(msr_value, bit)
    print(f"Bit {bit} value of msr {msr_address} = {bit_value}")
