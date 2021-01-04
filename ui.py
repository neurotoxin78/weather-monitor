import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.sparkline import Sparkline
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
import adafruit_logging as logging
logger = logging.getLogger('UI')
logger.setLevel(logging.INFO)

class UI(object):
    def __init__(self):
        # Fonts
        self.font_mini = terminalio.FONT
        self.font_middle = bitmap_font.load_font("fonts/font-middle.bdf")
        self.font_big = bitmap_font.load_font("fonts/font-big.bdf")
        self.font_verybig = bitmap_font.load_font("/sd/fonts/font-verybig.bdf")
        self.weather_font = bitmap_font.load_font("fonts/weather.bdf")
        displayio.release_displays()
        # Display init
        spi = busio.SPI(clock=board.LCD_CLK, MOSI=board.LCD_MOSI, MISO=board.LCD_MISO)
        while not spi.try_lock():
            pass
        spi.configure(baudrate=48000000, phase=0, polarity=0)
        spi.unlock()
        init_sequence = (
            b"\x01\x80\x80"  # Software reset then delay 0x80 (128ms)
            b"\xEF\x03\x03\x80\x02"
            b"\xCF\x03\x00\xC1\x30"
            b"\xED\x04\x64\x03\x12\x81"
            b"\xE8\x03\x85\x00\x78"
            b"\xCB\x05\x39\x2C\x00\x34\x02"
            b"\xF7\x01\x20"
            b"\xEA\x02\x00\x00"
            b"\xc0\x01\x23"  # Power control VRH[5:0]
            b"\xc1\x01\x10"  # Power control SAP[2:0];BT[3:0]
            b"\xc5\x02\x3e\x28"  # VCM control
            b"\xc7\x01\x86"  # VCM control2
            b"\x36\x01\x38"  # Memory Access Control
            b"\x37\x01\x00"  # Vertical scroll zero
            b"\x3a\x01\x55"  # COLMOD: Pixel Format Set
            # Frame Rate Control (In Normal Mode/Full Colors)
            b"\xb1\x02\x00\x18"
            b"\xb6\x03\x08\x82\x27"  # Display Function Control
            b"\xF2\x01\x00"  # 3Gamma Function Disable
            b"\x26\x01\x01"  # Gamma curve selected
            b"\xe0\x0f\x0F\x31\x2B\x0C\x0E\x08\x4E\xF1\x37\x07\x10\x03\x0E\x09\x00"  # Set Gamma
            b"\xe1\x0f\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F"  # Set Gamma
            b"\x11\x80\x78"  # Exit Sleep then delay 0x78 (120ms)
            b"\x29\x80\x78"  # Display on then delay 0x78 (120ms)
        )
        display_bus = displayio.FourWire(
            spi, command=board.LCD_D_C, chip_select=board.LCD_CS, reset=board.LCD_RST)
        self.display = displayio.Display(
            display_bus, init_sequence, width=320, height=240)
        self.display.rotation = 0
        logger.info('Display initialized')

    def main_screen(self, fg_color, bg_color):
        # UI
        _round = 10
        self.main_group = displayio.Group(max_size=25)
        self.display.show(self.main_group)
        self.display.auto_refresh = True
        self._background()
        self._bme_values(fg_color, bg_color)
        self._weather_values(0xffffff)
        self._status_bar(fg_color, bg_color)
        self._sparkline()
        self.show_labels()
        logger.info('UI Initialising ...')

    def _background(self):
        self.background = Rect(0, 0, 320, 240, fill=0x204a87)
        self.bme_panel = RoundRect(6, 6, 140, 40, 12, fill=0x19aeff, stroke=6)
        #self.bme_panel_shadow = RoundRect(8, 8, 140, 40, 5, fill=0x091834, stroke=6)
        self.border_panel = RoundRect(6, 75, 308, 4, 2, fill=0x19aeff, stroke=6)
        #self.border_panel_shadow = RoundRect(8, 77, 308, 5, 2, fill=0x091834, stroke=6)
        self.status_panel = Rect(0, 216, 320, 24, fill=0x19aeff)
        bitmap, palette = adafruit_imageload.load("images/home_circle_icon.ppm", bitmap=displayio.Bitmap, palette=displayio.Palette)
        self.home_icon = displayio.TileGrid(bitmap, pixel_shader=palette)
        self.home_icon.x = 10
        self.home_icon.y = 10
        self.main_group.append(self.background)
        #self.main_group.append(self.bme_panel_shadow)
        self.main_group.append(self.bme_panel)
        #self.main_group.append(self.border_panel_shadow)
        self.main_group.append(self.border_panel)
        self.main_group.append(self.status_panel)
        self.main_group.append(self.home_icon)
        logger.info('make background')

    def show_labels(self):
        self.main_group.append(self.temp_value)
        self.main_group.append(self.humi_value)
        self.main_group.append(self.out_temp)
        self.main_group.append(self.feels)
        self.main_group.append(self.wind)
        self.main_group.append(self.out_humi)
        self.main_group.append(self.we_desc_value)
        self.main_group.append(self.bounding_rectangle)
        self.main_group.append(self.sparkline)
        self.main_group.append(self.press_value)
        self.main_group.append(self.press_min_value)
        self.main_group.append(self.sys_stat_label)
        self.main_group.append(self.ip_label)
        self.main_group.append(self.countdown_label)
        logger.info('show labels')

    def _sparkline(self):
        # Baseline size of the sparkline chart, in pixels.
        chart_width = 185
        chart_height = 50
        line_color = 0xFFFFFF
        self.sparkline = Sparkline(width=chart_width, height=chart_height, max_items=600, x=10, y=88, color=line_color,)
        self.bounding_rectangle = RoundRect(self.sparkline.x - 3, self.sparkline.y - 3, chart_width + 6, chart_height + 6, 6, fill=0x2161AB, outline=0x5495DF)
        logger.info('create graphic')

    def add_graphic_value(self, x):
        self.display.auto_refresh = False
        self.sparkline.add_value(x)
        self.display.auto_refresh = True
        min_value = self.sparkline.values()
        #print(min_value)
        if min_value[0] < x:
            self.press_min_value._update_text("UP >")
        else:
            self.press_min_value._update_text("< DOWN")
            #self.press_min_value._update_text("{} mmHg".format(round(min_value[0] * 0.75)))

    def _weather_icon(self):
        pass

    def _weather_values(self, fill_color):
        value_y = 60
        # Out Temp
        self.out_temp = label.Label(self.font_big, text='+20 ' + chr(0176), color=fill_color)
        self.out_temp.x = 205
        self.out_temp.y = 25
        self.out_temp.scale = 1
        self.out_temp.anchor_point = (1, 0.5)

        # Feels like
        self.feels = label.Label(self.font_middle, text='??  ' + chr(0176), color=fill_color)
        self.feels.x = 150
        self.feels.y = 14
        self.feels.scale = 1

        # Wind Speed
        self.wind = label.Label(self.font_middle, text='??       ', color=fill_color)
        self.wind.x = 5
        self.wind.y = value_y
        self.wind.scale = 1

        # Humidity
        self.out_humi = label.Label(self.font_middle, text='100%  ', color=fill_color)
        self.out_humi.x = 150
        self.out_humi.y = 35
        self.out_humi.scale = 1

        # Weather Description Value
        self.we_desc_value = label.Label(self.font_middle, text='weather description                                   ', color=fill_color)
        self.we_desc_value.x = 150
        self.we_desc_value.y = value_y
        self.we_desc_value.scale = 1
        logger.info('make weather labels')

    def _bme_values(self, fill_color, outline_color):
        value_y = 26
        # Values Labels
        # Temp Value
        self.temp_value = label.Label(self.font_middle, text='20' + chr(0176), color=0xFFFFFF)
        self.temp_value.x = 48
        self.temp_value.y = value_y
        self.temp_value.scale = 1

        # Humidity Value
        self.humi_value = label.Label(self.font_middle, text="100" + chr(0x25), color=0xFFFFFF)
        self.humi_value.x = 85
        self.humi_value.y = value_y
        self.humi_value.scale = 1

        # Pressure Value
        self.press_value = label.Label(self.font_middle, text="000      ", color=fill_color)
        self.press_value.x = 205
        self.press_value.y = 94
        self.press_value.scale = 1
        # Pesure min value
        self.press_min_value = label.Label(self.font_middle, text="000      ", color=fill_color)
        self.press_min_value.x = 205
        self.press_min_value.y = 115
        self.press_min_value.scale = 1
        logger.info('make sensor label')

    def set_bme_values(self, temp, humi, press):
        self.temp_value._update_text("{}".format(str(round(temp))) + chr(0176))
        self.humi_value._update_text("{}".format(round(humi)) + "%")
        self.press_value._update_text("{} mmHg".format(round(press * 0.75)))

    def set_outside_temp(self, temp):
        self.out_temp._update_text(str(temp))
    def set_feels(self, temp):
        self.feels._update_text(str(temp))
    def set_outside_humidity(self, humi):
        self.out_humi._update_text(str(humi) + '%')
    def set_wind(self, speed, direction):
        self.wind._update_text(str(speed) + 'm/s ' + direction)
    def set_we_desc(self, desc):
        self.we_desc_value._update_text(str(desc))
    def _status_bar(self, fill_color, outline_color):
        label_y = 228
        self.sys_stat_label = label.Label(self.font_mini, text='RAM:         ', color=0x204a87)
        self.sys_stat_label.x = 10
        self.sys_stat_label.y = label_y
        self.sys_stat_label.scale = 1

        self.ip_label = label.Label(self.font_mini, text='IP:            ', color=0x204a87)
        self.ip_label.x = 145
        self.ip_label.y = label_y
        self.ip_label.scale = 1

        self.countdown_label = label.Label(self.font_mini, text='0000     ', color=0x204a87)
        self.countdown_label.x = 283
        self.countdown_label.y = label_y
        self.countdown_label.scale = 1
        logger.info('make status panel')

    def set_sys_stat(self, sys_stat):
        self.sys_stat_label._update_text(sys_stat)
    def set_ip_stat(self, ip):
        self.ip_label._update_text(ip)
    def set_countdown(self, count):
        self.countdown_label._update_text(count)
