import machine

# I2C address of the IS31FL3730
IS31FL3730_ADDR = 0x60

# I2C cloakc frequency for this device is 400kHz
IS31FL3730_I2C_FREQ = 400*1000

# Register addresses from the data sheet
REG_CONFIG = 0x00
REG_MATRX1_DATA_BASE = 0x01 # first column address of matrix1 - subsequent column data regs upto 0x0B inclusive
REG_MATRX2_DATA_BASE = 0x0E # first column address of matrix2 - subsequent column data regs upto 0x18 inclusive
REG_UPDATE_COLUMN = 0x0C
REG_LIGHTING_EFFECT = 0x0D
REG_PWM = 0x19
REG_RESET = 0xFF

"""
00h Configuration Register
The Configuration Register sets operation mode of IS31FL3730.

Bit     D7  D6:D5 D4:D3 D2   D1:D0
Name    SSD -     DM    A_EN ADM
Default 0   00    00    0    00

SSD Software Shutdown Enable
0 Normal operation
1 Software shutdown mode

DM Display Mode
00 Matrix 1 only
01 Matrix 2 only
11 Matrix 1 and Matrix 2

A_EN Audio Input Enable
0 Matrix intensity is controlled by the current
setting in the Lighting Effect Register (0Dh)
1 Enable audio signal to modulate the intensity
of the matrix

ADM Matrix Mode Selection
00 8×8 dot matrix display mode
01 7×9 dot matrix display mode
10 6×10 dot matrix display mode
11 5×11 dot matrix display mode
"""
REG_CONFIG_SSD_NORMAL = 0b00000000
REG_CONFIG_SSD_SHUTDOWN = 0b10000000
REG_CONFIG_DM_MATRIX1 = 0b00000000
REG_CONFIG_DM_MATRIX2 = 0b00001000
REG_CONFIG_DM_MATRIX1_AND_MATRIX2 = 0b00011000
REG_CONFIG_A_EN_DISABLED = 0b00000000
REG_CONFIG_A_EN_ENABLED  = 0b00000100
REG_CONFIG_ADM_8X8  = 0b00000000
REG_CONFIG_ADM_7X9  = 0b00000001
REG_CONFIG_ADM_6X10 = 0b00000010
REG_CONFIG_ADM_5X11 = 0b00000011

"""
0Dh Lighting Effect Register
Bit     D7 D6:D4 D3:D0
Name    -  AGS   CS
Default 0  000   0000

AGS Audio Input Gain Selection
000 Gain= 0dB
001 Gain= +3dB
010 Gain= +6dB
011 Gain= +9dB
100 Gain= +12dB
101 Gain= +15dB
110 Gain= +18dB
111 Gain= -6dB 

CS Full Current Setting for Each Row Output
0000 40mA
0001 45mA
... ...
0111 75mA
1000 5mA
1001 10mA
... ...
1110 35mA
Others Not Available
"""
REG_LIGHTING_EFFECT_AGS_0DB = 0b00000000
REG_LIGHTING_EFFECT_AGS_3DB = 0b00010000
REG_LIGHTING_EFFECT_AGS_6DB = 0b00100000
REG_LIGHTING_EFFECT_AGS_9DB = 0b00110000
REG_LIGHTING_EFFECT_AGS_12DB = 0b01000000
REG_LIGHTING_EFFECT_AGS_15DB = 0b01010000
REG_LIGHTING_EFFECT_AGS_18DB = 0b01100000
REG_LIGHTING_EFFECT_AGS_MINUS_6DB = 0b01110000

REG_LIGHTING_EFFECT_CS_40MA = 0b00000000
REG_LIGHTING_EFFECT_CS_45MA = 0b00000001
REG_LIGHTING_EFFECT_CS_75MA = 0b00000111
REG_LIGHTING_EFFECT_CS_5MA = 0b00001000
REG_LIGHTING_EFFECT_CS_10MA = 0b00001001
REG_LIGHTING_EFFECT_CS_35MA = 0b00001110

class IS31FL3730:
    def __init__(self, sclPin, sdaPin):
        self.__debug("constructor")
        self.i2c = machine.I2C(0,
                               scl=sclPin,
                               sda=sdaPin,
                               freq=IS31FL3730_I2C_FREQ)
        self.__check_device_present()
        self.__reset()
        
    def configure(self, ssd, dm, a_en, adm):
        self.__debug(f"configure ssd={ssd} dm={dm} a_en={a_en} adm={adm}")
        config_data = ssd | dm | a_en | adm
        self.__reg_write(REG_CONFIG, config_data)
        
    def __debug(self, msg):
        print(f"IS31FL3730 debug: {msg}")
        
    def __check_device_present(self):
        devices = self.i2c.scan()
        if IS31FL3730_ADDR not in devices:
            raise RuntimeError(f"No device found with I2C address {IS31FL3730_ADDR}")


    def __reg_write(self, reg, data):
      # Construct message
      msg = bytearray()
      msg.append(data)
    
      # Write out message to register
      self.i2c.writeto_mem(IS31FL3730_ADDR, reg, msg)

    # Set the data for a specific column of matrix 1. LED is on where bits are 1, off where bits are zero.
    # This function updates the internal data register but doesn't update the current display. A separate
    # call to update_display() us required to render the data registers onto the DISPLAY.
    #   column - a zero based index for the column to set
    #   data   - a single byte of data to write into the column's data register
    def set_matrix1_column_data(self, column, data):
        self.__debug(f"set_matrix1_column_data column={column} data={bin(data)}")
        self.__check_column_in_range(column)
        self.__reg_write(REG_MATRX1_DATA_BASE+column, data)

    def set_matrix2_column_data(self, column, data):
        self.__debug(f"set_matrix2_column_data column={column} data={bin(data)}")
        self.__check_column_in_range(column)
        self.__reg_write(REG_MATRX2_DATA_BASE+column, data)

    def set_lighting_effect(self,
                            ags = REG_LIGHTING_EFFECT_AGS_0DB,
                            cs = REG_LIGHTING_EFFECT_CS_40MA):
        self.__debug(f"set_lighting_effect ags={bin(ags)} cs={bin(cs)}")
        data = ags | cs
        self.__debug(f"set_lighting_effect data={bin(data)}")
        self.__reg_write(REG_LIGHTING_EFFECT, data)
        
    def update_display(self):
        self.__debug("update_display")
        self.__reg_write(REG_UPDATE_COLUMN, 0)

    def __check_column_in_range(self, column):
        if column < 0 or column > 10:
            raise RuntimeError(f"column index of {column} is out of range for this device - must be between 0 and 10 inclusive")
        
    def clear_matrix1_column_data(self):
        self.__debug("clear_matrix1_column_data")
        for column in range(0,10):
            self.set_matrix1_column_data(column, 0)

    def clear_matrix2_column_data(self):
        self.__debug("clear_matrix2_column_data")
        for column in range(0,10):
            self.set_matrix2_column_data(column, 0)

    def clear_all_column_data(self):
        self.__debug("clear_all_column_data")
        self.clear_matrix1_column_data()
        self.clear_matrix2_column_data()

    def __reset(self):
        self.__debug("reset")
        self.__reg_write(REG_RESET, 0)



