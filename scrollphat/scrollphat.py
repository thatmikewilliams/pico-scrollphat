from IS31FL3730 import IS31FL3730
from .font import font

class _col_buffer:
    def __init__(self):
        self.clear()
        
    def clear(self):
        self._buffer = [0] * 0
        self._col_ptr = 0
        
    def append(self, data):
        self._debug(f"append data={int(data)}")
        self._buffer.append(int(data))
        
    def inc_ptr(self):
        self._col_ptr += 1
        if int(self._col_ptr) >= len(self._buffer):
            self._col_ptr = 0
        self._debug(f"inc_ptr: col_ptr={self._col_ptr} len={len(self._buffer)}")

    def dec_ptr(self):
        self._col_ptr -= 1
        if int(self._col_ptr) < 0:
            self._col_ptr = len(self._buffer) - 1
        self._debug(f"dec_ptr: col_ptr={self._col_ptr} len={len(self._buffer)}")
    
    def _debug(self, msg):
        print(f"col_buffer: {msg}")
        
    def read_x_bytes(self, num_bytes):
        tmp_buffer = self._buffer.copy()
        
        padding_bytes = [0] * num_bytes
        tmp_buffer.extend(padding_bytes)
        
        x_bytes = tmp_buffer[self._col_ptr:self._col_ptr+num_bytes]
        self._debug(f"read_x_bytes: len(x_bytes)={len(x_bytes)}  x_bytes={x_bytes}")
        
        return x_bytes
    

class scrollphat:
    def __init__(self, sclPin, sdaPin, auto_update = False):
       
        self.controller = IS31FL3730.IS31FL3730(sclPin = sclPin,
                                                sdaPin = sdaPin)

        self.controller.configure(ssd = IS31FL3730.REG_CONFIG_SSD_NORMAL,
                                  dm = IS31FL3730.REG_CONFIG_DM_MATRIX1,
                                  a_en = IS31FL3730.REG_CONFIG_A_EN_DISABLED,
                                  adm = IS31FL3730.REG_CONFIG_ADM_5X11)

        self._auto_update = auto_update
        self._font = font
        self._buffer = _col_buffer()
        
        self.brightness_map = {
            1: IS31FL3730.REG_LIGHTING_EFFECT_CS_5MA,
            2: IS31FL3730.REG_LIGHTING_EFFECT_CS_10MA,
            3: IS31FL3730.REG_LIGHTING_EFFECT_CS_35MA,
            4: IS31FL3730.REG_LIGHTING_EFFECT_CS_40MA,
            5: IS31FL3730.REG_LIGHTING_EFFECT_CS_45MA,
            6: IS31FL3730.REG_LIGHTING_EFFECT_CS_75MA
        }

    
    def set_brightness(self, brightness):
        if brightness < 1 or brightness > 6:
            raise RuntimeError("brightness must be between 1 and 6 inclusive")
        
        self.controller.set_lighting_effect(cs = self.brightness_map[brightness])
        
    def update(self):
        self.controller.update_display()

    def write_string(self, msg):
          for char in msg:
            if ord(char) in self._font:
                font_char = self._font[ord(char)]
            else:
                font_char = self._font[ord('?')]
            
            for i in range(0, len(font_char)):
                self._buffer.append(font_char[i])
            
            char_padding = 0
            self._buffer.append(char_padding)

            self._set_column_data()
            
    def _set_column_data(self):
        col_data = self._buffer.read_x_bytes(11)
        for i in range(0, len(col_data)):
            self.controller.set_matrix1_column_data(i, col_data[i])
    
    def scroll_left(self):
        self._buffer.inc_ptr()
        self._set_column_data()

    def scroll_right(self):
        self._buffer.dec_ptr()
        self._set_column_data()


