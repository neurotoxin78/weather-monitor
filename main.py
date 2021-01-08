
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
# UI
theme = dark
ui = UI(theme)
ui.main_screen()
collect()
time.sleep(3)
# contrs and intervals
try_count = 0
weather_check_interval = 7200
minute_counter = weather_check_interval
graph_step = 100
graph_counter = graph_step

def degrees_to_cardinal(d):
    '''
    note: this is highly approximate...
    '''
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    #dirs = ["Пн", "ПнПнСх", "ПнСх", "СхПнСх", "Сх", "СхПдСх", "ПдСх", "ПдПдСх",
    #        "Пд", "ПдПдЗх", "ПдЗх", "ЗхПдЗх", "Зх", "ЗхПнЗх", "ПнЗх", "ПнПнЗх"]
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]

def set_weather(data):
    temperature, wind, weather = data['main'], data['wind'], data['weather']
    description= weather[0]
    raw_temp, raw_feels, humi, wind_speed, wind_deg, we_desc  = temperature['temp'], temperature['feels_like'], temperature['humidity'], wind['speed'], wind['deg'], description['description']
    wind_dir = degrees_to_cardinal(wind_deg)
    temp, feels = round(raw_temp), round(raw_feels)
    if temp > 0:
        ui.set_outside_temp("+" + str(round(temp)) + chr(0176))
    elif temp == 0:
        ui.set_outside_temp(" " + str(round(temp)) + chr(0176))
    else:
        ui.set_outside_temp(str(round(temp)) + chr(0176))
    if feels > 0:
        ui.set_feels("+" + str(round(feels)) + chr(0176))
    else:
        ui.set_feels(str(round(feels)) + chr(0176))
    ui.set_wind(wind_speed, wind_dir)
    ui.set_outside_humidity(humi)
    ui.set_we_desc(we_desc)
# Main Loop
logger.info('Start main loop')
while KeyboardInterrupt:
    ui.set_sys_stat("RAM:" + str(round(mem_free() / 1024 / 1024, 2)) + "Mb")
    ui.set_ip_stat('IP:' + str(dev.get_ip()))
    try:
        temp, humi, press = dev.get_temperature(), dev.get_humidity(), dev.get_pressure()
        #logger.info('get sensor data')
        if graph_counter == graph_step:
            ui.add_graphic_value(press)
            logger.info('add to graphics ' + str(press))
            graph_counter = 0
        else:
            graph_counter +=  1
        if temp != o_temp or humi != o_humi or press != o_press:
            ui.set_bme_values(temp, humi, press)
            o_temp, o_humi, o_press = temp, humi, press
    except:
        pass
    if minute_counter == weather_check_interval:
        data = dev.get_weather()
        if data != None:
            set_weather(data)
            logger.info('set current weather data')
            minute_counter = 0
        else:
            minute_counter = weather_check_interval - 30
            try_count += 1
#        if try_count == 5:
#            pass
#            #dev.reboot()
    else:
        minute_counter += 1
    ui.set_progress((minute_counter / weather_check_interval))
    ui.set_countdown(str(minute_counter))
    date_time = dev.get_datetime()
    ui.set_clock("{:0>2}".format(date_time[3] + 2) + ":{:0>2}".format(date_time[4]))
    collect()
    time.sleep(0.2)
