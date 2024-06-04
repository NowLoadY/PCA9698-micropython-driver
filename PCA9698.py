# Registers
INPUT_PORT_BANK0 = 0x00
OUTPUT_PORT_BANK0 = 0x08
POLARITY_INVERSION_BANK0 = 0x10
POLARITY_INVERSION_BANK1 = 0x11
POLARITY_INVERSION_BANK2 = 0x12
POLARITY_INVERSION_BANK3 = 0x13
POLARITY_INVERSION_BANK4 = 0x14
IO_CONFIG_BANK0 = 0x18
MASK_INTERRUPT_BANK0 = 0x20
MASK_INTERRUPT_BANK1 = 0x21
MASK_INTERRUPT_BANK2 = 0x22
MASK_INTERRUPT_BANK3 = 0x23
MASK_INTERRUPT_BANK4 = 0x24
OUTPUT_CONFIG = 0x28
ALL_BANK = 0x29
MODE = 0x2A
AUTO_INCREMENT = 0x80
MODE_SMBA = 0x10
MODE_IOAC = 0x08
MODE_OCH = 0x02
MODE_OEPOL = 0x01

class PCA9698:
    def __init__(self, iic, address=0x20):
        self.iic = iic
        self.address = address
        self.output_port = bytearray(5)
        self.input_port = bytearray(5)
        self.mode = bytearray(5)

    def set_pin_mode(self, pin, mode):
        port_num = pin // 8
        command = IO_CONFIG_BANK0 + port_num
        current_mode = self.read_port_mode(port_num)
        if mode == 1:
            new_mode = current_mode & ~(1 << (pin % 8))
        else:
            new_mode = current_mode | (1 << (pin % 8))
        self.iic.writeto(self.address, bytes([command, new_mode]))

    def read_pin(self, pin):
        port_num = pin // 8
        command = INPUT_PORT_BANK0 + port_num
        self.iic.writeto(self.address, bytes([command]))
        result = self.iic.readfrom(self.address, 1)
        return (result[0] >> (pin % 8)) & 0x01

    def write_pin(self, pin, value):
        port_num = pin // 8
        command = OUTPUT_PORT_BANK0 + port_num
        current_state = self.read_port(port_num)
        if value == 1:
            new_state = current_state | (1 << (pin % 8))
        else:
            new_state = current_state & ~(1 << (pin % 8))
        
        self.iic.writeto(self.address, bytes([command, new_state]))
        
        # # 读取回写状态
        # self.iic.writeto(self.address, bytes([command]))
        # result = self.iic.readfrom(self.address, 1)
        # read_back_state = (result[0] >> (pin % 8)) & 0x01
        
        # return read_back_state

    def set_port_mode(self, port_num, mode):
        if port_num >= 5:
            raise ValueError("port_num must be between 0 and 4")
        command = IO_CONFIG_BANK0 + port_num
        if mode == 1:
            new_mode = 0x00  # ALL SET OUTPUT
        else:
            new_mode = 0xFF  # ALL SET INPUT
        try:
            self.iic.writeto(self.address, bytes([command, new_mode]))
        except Exception as e:
            print(f"Failed to set port mode: {e}")

    def set_ports_mode(self, modes):
        if len(modes) != 5:
            raise ValueError("Modes array must contain exactly 5 elements.")
        for port_num, mode in enumerate(modes):
            self.set_port_mode(port_num, mode)
            print(f"Set port {port_num} to mode {mode}")

    def read_port(self, port_num):
        if port_num >= 5:
            return 0
        command = INPUT_PORT_BANK0 + port_num
        self.iic.writeto(self.address, bytes([command]))
        result = self.iic.readfrom(self.address, 1)
        return result[0]
    
    def read_port_mode(self, port_num):
        if port_num >= 5:
            return 0
        command = IO_CONFIG_BANK0 + port_num
        self.iic.writeto(self.address, bytes([command]))
        result = self.iic.readfrom(self.address, 1)
        return result[0]

    def update_all(self):
        self.iic.writeto(self.address, bytes([OUTPUT_PORT_BANK0 | AUTO_INCREMENT]))
        self.iic.readfrom_into(self.address, self.output_port, 5)
        self.iic.writeto(self.address, bytes([INPUT_PORT_BANK0 | AUTO_INCREMENT]))
        self.iic.readfrom_into(self.address, self.input_port, 5)

    def toggle_all_ports(self):
        """
        Toggles all output ports by inverting their current state.
        """
        for port_num in range(5):
            current_state = self.read_port(port_num)
            new_state = ~current_state & 0xFF  # Assuming 8-bit ports
            self.iic.writeto(self.address, bytes([OUTPUT_PORT_BANK0 + port_num, new_state]))
    
    def set_interrupt(self, pin, enable):
        port_num = pin // 8
        command = MASK_INTERRUPT_BANK0 + port_num
        current_mask = self.read_interrupt_mask(port_num)
        if enable:
            new_mask = current_mask | (1 << (pin % 8))
        else:
            new_mask = current_mask & ~(1 << (pin % 8))
        self.iic.writeto(self.address, bytes([command, new_mask]))

    def read_interrupt_mask(self, port_num):
        if port_num >= 5:
            return 0
        command = MASK_INTERRUPT_BANK0 + port_num
        self.iic.writeto(self.address, bytes([command]))
        result = self.iic.readfrom(self.address, 1)
        return result[0]

    def set_interrupt_port(self, port_num, mask):
        if port_num >= 5:
            raise ValueError("port_num must be between 0 and 4")
        command = MASK_INTERRUPT_BANK0 + port_num
        self.iic.writeto(self.address, bytes([command, mask]))

    def set_interrupt_ports(self, masks):
        if len(masks) != 5:
            raise ValueError("Masks array must contain exactly 5 elements.")
        for port_num, mask in enumerate(masks):
            self.set_interrupt_port(port_num, mask)
            print(f"Set interrupt mask for port {port_num} to {mask}")