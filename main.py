import machine
import utime
from scrollphat import scrollphat
from IS31FL3730 import IS31FL3730


buffer = [1] * 11
print(buffer)
buffer += [4] * (-3)
print(buffer)

scrollphat = scrollphat.scrollphat(sclPin = machine.Pin(17),
                                   sdaPin = machine.Pin(16))


scrollphat.set_brightness(2)

scrollphat.write_string("hello world! ")
scrollphat.update()

for i in range(0, 500):
    scrollphat.scroll_left()
    scrollphat.update()
    utime.sleep_ms(100)


