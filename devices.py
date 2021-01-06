import adafruit_bme280
import board
import busio
import wifi
import socketpool
import ssl
import adafruit_requests
from microcontroller import reset
import digitalio
import sdcardio
import storage
import adafruit_logging as logging
import rtc
logger = logging.getLogger('devices')
logger.setLevel(logging.INFO)

class Devices(object):
    def __init__(self):
        # bme280
        i2c2 = busio.I2C(board.IO39, board.IO33)
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c2, address=0x76)
        logger.info('BME280 sensor initialized')
        self.bme280.sea_level_pressure = 1016.2
        self.bme280.mode = adafruit_bme280.MODE_NORMAL
        self.bme280.standby_period = adafruit_bme280.STANDBY_TC_500
        self.bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
        self.bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
        self.bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
        self.bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2
        logger.info('BME280 sensor configured')
        self.pwr_pin = digitalio.DigitalInOut(board.IO14)
        self.pwr_pin.direction = digitalio.Direction.OUTPUT
        logger.info('power pin configured')
        #SD
        self.sd_power_on()
        spi = busio.SPI(clock=board.SD_CLK, MOSI=board.SD_MOSI, MISO=board.SD_MISO)
        sd = sdcardio.SDCard(spi, board.SD_CS)
        vfs = storage.VfsFat(sd)
        storage.mount(vfs, '/sd')
        logger.info('SD Card initialized and mount /sd')

    def sd_power_on(self):
        self.pwr_pin.value = 1

    def sd_power_off(self):
        self.pwr_pin.value = 0

    def reboot(self):
        reset()

    def connect(self, ssid, passwd):
        wifi.radio.connect(ssid=ssid, password=passwd)
        self.pool = socketpool.SocketPool(wifi.radio)
        self.request = adafruit_requests.Session(self.pool, ssl.create_default_context())
        logger.info('Wi-Fi connected')

    def ntptime(self):
        response = self.request.get("http://worldclockapi.com/api/json/est/now")
        if response.status_code == 200:
            r = rtc.RTC()
            r.datetime = time.localtime(response.json()['currentFileTime'])
            print(f"System Time: {r.datetime}")
            logger.error(f"System Time: {r.datetime}")
        else:
            print("Setting time failed")
            logger.error('Setting time faled')

    def get_ip(self):
        return wifi.radio.ipv4_address
    def get_weather(self):
        try:
            response = self.request.get("http://api.openweathermap.org/data/2.5/weather?q=Pozniaky&units=metric&appid=e71be9fbe7496e8dc2127b9f08afd114&lang=ua")
            data = response.json()
            logger.info('get request from openweathermap')
            return data
        except:
            return None

    def update_weather(self):
        data = self.get_weather()
        if data != None:
            c_w = data['current']
            logger.info('weather info updated')
            return c_w['temperature'], c_w['feelslike'], c_w['humidity'], c_w['wind_speed'], c_w['wind_dir'], c_w['weather_descriptions']
        else:
            logger.error('error while update weather data')
            return 0, 0, 0, 0, 0, ['error']

    def get_temperature(self):
        return self.bme280.temperature

    def get_humidity(self):
        return self.bme280.humidity

    def get_pressure(self):
        return self.bme280.pressure

    def get_altitude(self):
        return self.bme280.altitude
