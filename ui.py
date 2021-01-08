import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.sparkline import Sparkline
from adafruit_progressbar import ProgressBar
from adafruit_bitmap_font import bitmap_font
import adafruit_logging as logging
logger = logging.getLogger('UI')
logger.setLevel(logging.INFO)

class UI(object):
    def __init__(self, theme):
        # themes
        self.theme = theme
        # Fonts
        self.font_default = terminalio.FONT
        self.font_micro = bitmap_font.load_font("fonts/font-6.bdf")
        self.font_mini = bitmap_font.load_font("fonts/font-8.bdf")
        self.font_normal = bitmap_font.load_font("fonts/font-12.bdf")
        self.font_middle = bitmap_font.load_font("fonts/font-middle.bdf")
        self.font_big = bitmap_font.load_font("/sd/fonts/font-big.bdf")
        self.icons_10 = bitmap_font.load_font("fonts/awesome_icons-10.bdf")
        self.icons_12 = bitmap_font.load_font("fonts/awesome_icons-12.bdf")
        self.icons_16 = bitmap_font.load_font("fonts/awesome_icons-16.bdf")

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

    def main_screen(self):
        # UI
        _round = 10
        self.main_group = displayio.Group(max_size=25)
        self.display.show(self.main_group)
        self.display.auto_refresh = True
        self._background()
        self._bme_values()
        self._weather_values()
        self._status_bar()
        self._progress_bar()
        self._sparkline()
        self._clock()
        self.show_ui()
        logger.info('UI Initialising ...')

    def _background(self):
        self.background = Rect(0, 0, 320, 240, fill=self.theme['background'])
        self.border_panel = Rect(6, 65, 308, 3, fill=self.theme['top_panel'], stroke=6)
        self.border_panel_next = Rect(6, 120, 308, 3, fill=self.theme['top_panel'], stroke=6)
        self.status_panel = Rect(0, 216, 320, 24, fill=self.theme['bottom_panel'])
        logger.info('make background')

    def show_ui(self):
        self.main_group.append(self.background)
        #self.main_group.append(self.bme_panel)
        self.main_group.append(self.border_panel)
        self.main_group.append(self.border_panel_next)
        self.main_group.append(self.status_panel)
        self.main_group.append(self.temp_value)
        self.main_group.append(self.humi_value)
        self.main_group.append(self.out_temp)
        self.main_group.append(self.feels)
        self.main_group.append(self.wind_icon)
        self.main_group.append(self.wind)
        self.main_group.append(self.out_humi)
        self.main_group.append(self.we_desc_value)
        self.main_group.append(self.bounding_rectangle)
        self.main_group.append(self.sparkline)
        self.main_group.append(self.press_value)
        self.main_group.append(self.press_min_value)
        self.main_group.append(self.sys_stat_label)
        self.main_group.append(self.ip_label)
        self.main_group.append(self.progress_bar)
        self.main_group.append(self.countdown_label)
        self.main_group.append(self.clock_label)
        logger.info('show labels')

    def _clock(self):
        self.clock_label = label.Label(self.font_middle, text='00:00                               ' + chr(0176), color=self.theme['text_color'])
        self.clock_label.x = 130
        self.clock_label.y = 228
        self.clock_label.scale = 1
        self.clock_label.anchor_point = (1, 0.5)

    def _progress_bar(self):
        self.progress_bar = ProgressBar(0, 210, 320, 6, 0.0, bar_color=self.theme['top_panel'], outline_color=self.theme['background'], stroke=4)
        #self.progress_bar.fill = self.theme['background']

    def set_progress(self, progress):
        self.progress_bar.progress = progress

    def _sparkline(self):
        chart_width = 200
        chart_height = 40
        x = 10
        y = 74
        line_color = self.theme['spark_line']
        self.sparkline = Sparkline(width=chart_width, height=chart_height, max_items=chart_width, x=x, y=y, color=line_color,)
        self.bounding_rectangle = Rect(self.sparkline.x - 3, self.sparkline.y - 3, chart_width + 6, chart_height + 6, fill=self.theme['graphic_background'], outline=self.theme['graphic_background'])
        logger.info('create graphic')

    def add_graphic_value(self, x):
        self.display.auto_refresh = False
        self.sparkline.add_value(x)
        self.display.auto_refresh = True
        min_value = self.sparkline.values()
        #print(min_value)
        if min_value[0] < x:
            self.press_min_value._update_text("B")
        else:
            self.press_min_value._update_text("A")
            #self.press_min_value._update_text("{} mmHg".format(round(min_value[0] * 0.75)))


    def _weather_values(self):
        value_y = 52
        # Out Temp
        self.out_temp = label.Label(self.font_big, text='+20 ' + chr(0176), color=self.theme['text_color'])
        self.out_temp.x = 210
        self.out_temp.y = 25
        self.out_temp.scale = 1
        self.out_temp.anchor_point = (1, 0.5)

        # Feels like
        self.feels = label.Label(self.font_middle, text='??  ' + chr(0176), color=self.theme['text_color'])
        self.feels.x = 154
        self.feels.y = 12
        self.feels.scale = 1

        # Wind Speed
        self.wind = label.Label(self.font_normal, text='??       ', color=self.theme['text_color'])
        self.wind.x = 30
        self.wind.y = value_y
        self.wind.scale = 1
        # Wind icon
        self.wind_icon = label.Label(self.icons_10, text='G', color=self.theme['text_color'])
        self.wind_icon.x = 8
        self.wind_icon.y = value_y + 6

        # Humidity
        self.out_humi = label.Label(self.font_middle, text='100%  ', color=self.theme['text_color'])
        self.out_humi.x = 150
        self.out_humi.y = 33
        self.out_humi.scale = 1

        # Weather Description Value
        self.we_desc_value = label.Label(self.font_normal, text='weather description                                   ', color=self.theme['text_color'])
        self.we_desc_value.x = 150
        self.we_desc_value.y = value_y
        self.we_desc_value.scale = 1
        logger.info('make weather labels')

    def _bme_values(self):
        value_y = 20
        # Values Labels
        # Temp Value
        self.temp_value = label.Label(self.icons_16, text='D20' + chr(0176), color=self.theme['text_color'])
        self.temp_value.x = 5
        self.temp_value.y = value_y
        self.temp_value.scale = 1

        # Humidity Value
        self.humi_value = label.Label(self.icons_16, text="E100" + chr(0x25), color=self.theme['text_color'])
        self.humi_value.x = 62
        self.humi_value.y = value_y
        self.humi_value.scale = 1

        # Pressure Value
        self.press_value = label.Label(self.icons_16, text="F000      ", color=self.theme['text_color'])
        self.press_value.x = 248
        self.press_value.y = 102
        self.press_value.scale = 1
        # Pesure min value
        self.press_min_value = label.Label(self.icons_16, text="    ", color=self.theme['text_color'])
        self.press_min_value.x = 222
        self.press_min_value.y = 105
        self.press_min_value.scale = 1
        logger.info('make sensor label')

    def set_bme_values(self, temp, humi, press):
        self.temp_value._update_text("D {}".format(str(round(temp))) + chr(0176))
        self.humi_value._update_text("E {}".format(round(humi)))
        self.press_value._update_text("F {}".format(round(press * 0.75)))

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
    def _status_bar(self):
        label_y = 228
        self.sys_stat_label = label.Label(self.font_mini, text='RAM:         ', color=self.theme['mem_free_label'])
        self.sys_stat_label.x = 6
        self.sys_stat_label.y = label_y
        self.sys_stat_label.scale = 1

        self.ip_label = label.Label(self.font_mini, text='IP:            ', color=self.theme['ip_label'])
        self.ip_label.x = 200
        self.ip_label.y = label_y
        self.ip_label.scale = 1

        self.countdown_label = label.Label(self.font_mini, text='0000     ', color=self.theme['counter'])
        self.countdown_label.x = 290
        self.countdown_label.y = label_y
        self.countdown_label.scale = 1
        logger.info('make status panel')

    def set_sys_stat(self, sys_stat):
        self.sys_stat_label._update_text(sys_stat)
    def set_ip_stat(self, ip):
        self.ip_label._update_text(ip)
    def set_countdown(self, count):
        self.countdown_label._update_text(count)
    def set_clock(self, time):
        self.clock_label._update_text(str(time))
