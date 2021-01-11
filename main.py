from utils import degrees_to_cardinal
import gc
import os
import time
from gc import collect, mem_free
from ui import UI
from devices import Devices
import random
import adafruit_logging as logging
from themes import *
import supervisor as s
s.disable_autoreload()

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
time.sleep(3)
# Devices
dev = Devices()
# UI
theme = dark
ui = UI(theme)
#WiFi
ssid = "Neurotoxin2"
passwd = "Mxbb2Col"
try:
    dev.connect(ssid, passwd)
except:
    pass
#dev.ntptime()
# Variables
o_temp = 0
o_humi = 0
o_press = 0
o_alt = 0
collect()
time.sleep(3)
# counters and intervals
try_count = 0
weather_check_interval = 7200
minute_counter = weather_check_interval
graph_step = 100
graph_counter = graph_step


def set_weather(data):
    temperature, wind, weather = data['main'], data['wind'], data['weather']
    description= weather[0]
    raw_temp, raw_feels, humi, wind_speed, wind_deg, we_desc  = temperature['temp'], temperature['feels_like'], temperature['humidity'], wind['speed'], wind['deg'], description['description']
    wind_dir = degrees_to_cardinal(wind_deg)
    temp, feels = round(raw_temp), round(raw_feels)
    if temp > 0:
        t = "+" + str(round(temp)) + chr(0176)
    elif temp == 0:
        t = " " + str(round(temp)) + chr(0176)
    else:
        t = str(round(temp)) + chr(0176)
    if feels > 0:
        f = "+" + str(round(feels)) + chr(0176)
    else:
        f = str(round(feels)) + chr(0176)
    ui.set_weather_values(t, f, humi, wind_speed, wind_dir, we_desc)

def set_forecast(arg):
    fc = arg['daily'][1]
    dt = time.localtime(fc['dt'])
    _date_ = "{:0>2}".format(dt[2]) + ".{:0>2}".format(dt[1]) + ".{:0>4}".format(dt[0])
    temp = fc['temp']
    day_temp, night_temp = temp['day'], temp['night']
    feels_like = fc['feels_like']
    feels_day, feels_night = feels_like['day'], feels_like['night']
    humidity, pressure = fc['humidity'], fc['pressure'] * 0.75
    humi = ui.HUMI_ICO + str(round(humidity))
    press = ui.PRES_ICO + str(round(pressure))
    wind_speed, wind_deg = fc['wind_speed'], fc['wind_deg']
    wind = ui.WIND_ICO + str(round(wind_speed)) + " " + str(degrees_to_cardinal(wind_deg))
    dn_temp = ui.DAYZ_ICO + str(round(day_temp)) + ui.NIGT_ICO + str(round(night_temp))
    description = fc['weather'][0]['description']
    ui.set_forecast_values(_date_, dn_temp, wind, press, humi, description)


#set_forecast(dev.get_forecast())
# Main Loop
logger.info('Start main loop')
ui.main_screen()
while KeyboardInterrupt:
    ui.set_sys_stat("RAM:" + str(round(mem_free() / 1024 / 1024, 2)) + "Mb")
    ui.set_ip_stat('IP:' + str(dev.get_ip()))
    try:
        temp, humi, press = dev.get_temperature(), dev.get_humidity(), dev.get_pressure()
        #logger.info('get sensor data')
        if graph_counter == graph_step:
            ui.add_graphic_value(press)
            logger.info('add to graph: ' + str(press))
            ui.logit('update graph')
            graph_counter = 0
        else:
            graph_counter +=  1
        if temp != o_temp or humi != o_humi or press != o_press:
            ui.set_bme_values(temp, humi, press)
            o_temp, o_humi, o_press = temp, humi, press
    except:
        pass
    if minute_counter == weather_check_interval:
        ui.logit('getting current weather')
        data = dev.get_weather()
        if data != None:
            set_weather(data)
            logger.info('set current weather data')
            ui.logit('display weather')
            minute_counter = 0
        else:
            minute_counter = weather_check_interval - 30
            try_count += 1
        ui.logit('getting forecast')
        forecast = dev.get_forecast()
        if forecast != None:
            ui.logit('display forecast')
            set_forecast(forecast)
            logger.info('set forecast')
        else:
            try_count += 1
    else:
        minute_counter += 1
    ui.set_progress((minute_counter / weather_check_interval))
    #ui.set_countdown(str(minute_counter))
    ui.logit('wait {} sec'.format(weather_check_interval - minute_counter))
    date_time = dev.get_datetime()
    ui.set_clock("{:0>2}".format(date_time[3] + 2) + ":{:0>2}".format(date_time[4]))
    collect()
    time.sleep(0.2)
