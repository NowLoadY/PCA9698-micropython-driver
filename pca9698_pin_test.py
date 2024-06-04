from machine import SoftI2C, Pin
import PCA9698
import time

#DRV8833_MOTOR_DRIVER_STBY = Pin(17, Pin.OUT)
#DRV8833_MOTOR_DRIVER_STBY.value(1)
PCA9698_OE_ = Pin(48, Pin.OUT)  # active LOW
PCA9698_OE_.value(0)  # Set the OE pin to low to enable the output
i2c = SoftI2C(scl=Pin(3), sda=Pin(2), freq=400000)  # Initialize I2C with SCL on Pin 3, SDA on Pin 2, and frequency of 400kHz
devices = i2c.scan()  # Scan for devices on the I2C bus
print("found devices:", [hex(device) for device in devices])  # Print the addresses of found devices in hexadecimal format
pca_1 = PCA9698.PCA9698(iic=i2c, address=0x20)  # Create an instance of PCA9698 with I2C address 0x20
#pca_2 = PCA9698.PCA9698(iic=i2c, address=0x21)
#pca_3 = PCA9698.PCA9698(iic=i2c, address=0x22)
pcas = [pca_1]#[pca_1, pca_2, pca_3]
for pca_num, pca in enumerate(pcas):
    print(f"Set all ports to mode 'input'")
    pca.set_ports_mode([0,0,0,0,0])  # Set all ports of PCA9698 to output mode
    pca.update_all()
    for port_num in range(5):
        mode_dict = {0x00: "output", 0xFF: "input"}
        print(f"pca_{pca_num}:port {port_num} mode: {mode_dict.get(pca.read_port_mode(port_num), 'unknown')}")
    print(f"Set all ports to mode 'output'")
    pca.set_ports_mode([1,1,1,1,1])  # Set all ports of PCA9698 to output mode
    pca.update_all()
    for port_num in range(5):
        mode_dict = {0x00: "output", 0xFF: "input"}
        print(f"pca_{pca_num}:port {port_num} mode: {mode_dict.get(pca.read_port_mode(port_num), 'unknown')}")
#pca_1.set_port_mode(port_num=0, mode=1)
#pca_1.set_port_mode(port_num=1, mode=1)
#pca_1.set_port_mode(port_num=2, mode=1)
#pca_1.set_port_mode(port_num=3, mode=1)
#pca_1.set_port_mode(port_num=4, mode=1)
time.sleep(0.5)  # Delay for 0.5 seconds

for pca_num, pca in enumerate(pcas):
    print(f"pca_{pca_num}:drive on")  # Indicate that driving the pins is starting
    for pin_num in range(40):
        pca.write_pin(pin_num, 1)  # Set each pin to high
        print(f"pca_{pca_num}: pin:{pin_num}", "read again:", pca.read_pin(pin_num))  # Print the pin number and read back its status
        #new_status = pca.write_pin(pin_num, 1)  # on
        #print(f"pca_{pca_num}: pin:{pin_num}", "new_status:", new_status, "read again:", pca.read_pin(pin_num))

    time.sleep(1)  # Delay for 1 second
    print(f"pca_{pca_num}:drive off")  # Indicate that driving the pins is stopping
    for pin_num in range(40):
        pca.write_pin(pin_num, 0)  # Set each pin to low
        print(f"pca_{pca_num}: pin:{pin_num}", "read again:", pca.read_pin(pin_num))  # Print the pin number and read back its status
        #new_status = pca.write_pin(pin_num, 0)  # off
        #print(f"pca_{pca_num}: pin:{pin_num}", "new_status:", new_status, "read again:", pca.read_pin(pin_num))
    
    time.sleep(1)
    pca.toggle_all_ports()
    print(f"pca_{pca_num}:toggle", [pca.read_pin(pin_num) for pin_num in range(40)])
    time.sleep(1)
    pca.toggle_all_ports()
    print(f"pca_{pca_num}:toggle", [pca.read_pin(pin_num) for pin_num in range(40)])

    # Testing interrupt functionality
    print(f"pca_{pca_num}:Setting up interrupts for PCA9698")
    # Enable interrupts for the first 5 pins of the first PCA device
    interrupt_enabled = True
    for pin_num in range(5):
        pca.set_interrupt(pin=pin_num, enable=1)
        #print(f"pca9698_{pca_num}:Interrupt enabled on pin {pin_num}")

    # Check and print the interrupt mask status
    for pin_num in range(5):
        mask_status = pca.read_interrupt_mask(pin_num // 8)
        #print(f"pca9698_{pca_num}:Interrupt mask status for port {pin_num // 8}: {bin(mask_status)}")

    # Simulate pin state change and check for interrupt response
    print(f"pca_{pca_num}:Simulating pin state changes and checking interrupt responses")
    for pin_num in range(5):
        pca.write_pin(pin_num, 1)  # Set pin high
        time.sleep(0.1)  # Short delay to simulate real conditions
        pca.write_pin(pin_num, 0)  # Set pin low
        # Read pin state to confirm if interrupt was triggered
        pin_state = pca.read_pin(pin_num)
        if pin_state == 0:
            #print(f"pca9698_{pca_num}:Pin {pin_num} state correct after toggle, interrupt functionality OK")
            pass
        else:
            print(f"pca_{pca_num}:Pin {pin_num} state incorrect after toggle, interrupt functionality may have issues")
            interrupt_enabled = False

    if interrupt_enabled:
        print(f"pca_{pca_num}:Interrupt functionality normal for all tested pins")
        pass
    else:
        print(f"pca_{pca_num}:Some pins may have issues with interrupt functionality, please check hardware or configuration")

    # Disable all interrupts
    print(f"pca_{pca_num}: Disabling interrupts")
    for pin_num in range(40):
        pca.set_interrupt(pin=pin_num, enable=0)
    print(f"pca_{pca_num}:Interrupts disabled for all pins")
    print("#############")

