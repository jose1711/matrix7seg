class Matrix7seg:

    _NOOP = 0
    _DIGIT0 = 1
    _DIGIT1 = 2
    _DIGIT2 = 3
    _DIGIT3 = 4
    _DIGIT4 = 5
    _DIGIT5 = 6
    _DIGIT6 = 7
    _DIGIT7 = 8
    _DECODEMODE = 9
    _INTENSITY = 10
    _SCANLIMIT = 11
    _SHUTDOWN = 12
    _DISPLAYTEST = 15

    _DIGITS = {
        ' ': 0x00,
        '-': 0x01,
        '0': 0x7e,
        '1': 0x30,
        '2': 0x6d,
        '3': 0x79,
        '4': 0x33,
        '5': 0x5b,
        '6': 0x5f,
        '7': 0x70,
        '8': 0x7f,
        '9': 0x7b,
        'A': 0x77,
        'B': 0x1f,
        'C': 0xd,
        'D': 0x3d,
        'E': 0x4f,
        'F': 0x47,
        'G': 0x5e,
        'H': 0x17,
        'I': 0x10,
        'J': 0x3c,
        'K': 0x2f,
        'L': 0xe,
        'M': 0x54,
        'N': 0x15,
        'O': 0x1d,
        'P': 0x67,
        'Q': 0x73,
        'R': 0x5,
        'S': 0x5b,
        'T': 0xf,
        'U': 0x1c,
        'V': 0x2a,
        'W': 0x2a,
        'X': 0x37,
        'Y': 0x33,
        'Z': 0x6d,
    }

    _ROT_DIGITS = {
        '0': 0x1d,
        '1': 0x8,
        '2': 0x25,
        '3': 0x1c,
        '4': 0xd,
        '5': 0x13,
        '6': 0x5,
        '7': 0x18,
        '8': 0x14,
        '9': 0x98,
        ' ': 0x0,
    }

    NUM_DIGITS = 8

    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.buffer = bytearray(8)
        spi.init()
        self.init()

    def _register(self, command, data):
        # write to display
        try:
            self.cs.write_digital(0)
        except:
            self.cs.off()
        except:
            self.cs.value(0)
        self.spi.write(bytearray([command, data]))
        try:
            self.cs.write_digital(0)
        except:
            self.cs.on()
        except:
            self.cs.value(1)

    def init(self):
        for command, data in (
            (self._SHUTDOWN, 0),
            (self._DISPLAYTEST, 0),
            (self._SCANLIMIT, 7),
            (self._DECODEMODE, 0),
            (self._SHUTDOWN, 1),
        ):
            self._register(command, data)

    def write_number(self, value, zeroPad=False, leftJustify=False, rotate=False):
        # Take number, format it, look up characters then pass to buffer.
        # rotate=True will result in a number rotated by 90 degrees.
        # Due to the display limitation some numbers may be difficult
        # to interpret at a glance (#4 or #6 for instance)

        if len(str(value)) > self.NUM_DIGITS:
            raise OverflowError('{0} too large for display'.format(value))

        size = self.NUM_DIGITS
        formatStr = '%'

        if zeroPad:
            formatStr += '0'

        if leftJustify:
            size *= -1

        formatStr = '{fmt}{size}i'.format(fmt=formatStr, size=size)
        position = self._DIGIT7
        strValue = formatStr % value

        if rotate:
            table = self._ROT_DIGITS
            strValue = ''.join(reversed([x for x in strValue]))
        else:
            table = self._DIGITS

        # look up each digit's character
        # then send to buffer
        for char in strValue:
            self.buffer[position - 1] = self.letter(char, table=table)
            position -= 1

    def write_string(self, value, zeroPad=False, leftJustify=False):
        # Take string, format it, look up characters then pass to buffer.

        if len(str(value)) > self.NUM_DIGITS:
            raise OverflowError('{0} too large for display'.format(value))

        size = self.NUM_DIGITS
        formatStr = '%'

        if zeroPad:
            formatStr += '0'

        if leftJustify:
            size *= -1

        formatStr = '{fmt}{size}s'.format(fmt=formatStr, size=size)
        position = self._DIGIT7
        strValue = formatStr % value

        # look up each digit's character
        # then send to buffer
        for char in strValue.upper():
            self.buffer[position - 1] = self.letter(char)
            position -= 1

    def write_raw(self, position, value):
        """Write to display directly - can be used to light
           up arbitrary combination of LED segments"""
        if position > self.NUM_DIGITS:
            raise OverflowError('position {0} outside display'.format(position))
        self.buffer[position - 1] = value

    def clear(self):
        """Clear display"""
        for pos in range(1, self.NUM_DIGITS + 1):
            self.write_raw(pos, 0)
        self.show()

    def letter(self, char, table=None):
        # Look up character on digits table & return
        if table is None:
            table = self._DIGITS
        value = table.get(str(char))
        return value

    def show(self, positions=8):
        for y in range(positions):
            self._register(self._DIGIT0 + y, self.buffer[y])
