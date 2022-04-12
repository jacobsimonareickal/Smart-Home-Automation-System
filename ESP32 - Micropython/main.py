# Project Name        - Home Automation Using ESP32 and Micropython
# Project Author      - Jacob Simon Areickal
# Project Version     - 1.0.0
# Project Description - A basic home automation project using ESP32 and micropython. This project lets you control multiple relays from cloud and will also display temperature and humidity using DHT22 sensor
# Project Code Core Module Changes
#   1. 22-Mar-2022 - Added Email Functionality For High Temperature Reading
#   2. 22-Mar-2022 - Added timestamp functionality for logging and debugging
#   3. 24-Mar-2022 - Added live weather functionality using OpenWeather API
#   4. 25-Mar-2022 - Changed relay switching logic for easy debugging and reduced time complexity
#   5. 25-Mar-2022 - Added functionality which sends GET to WorlTimeAPI to return current local time. ESP32 will still be able to get local time even when not connected to PC due to this addition.
#   6. 26-Mar-2022 - Added an LED blink function for the on board LED to notify when ESP is connected and Blynk and registering Blynk events

# Defects detected and needed to be worked on:
#     1. Unable to handle https requests. ESP32 returns out of memory error when requests are made using https
#     2. Need to fix project source code's time complexity and make it more memory efficient.
#     3. Need to implement more exception handling to handle exceptions during runtime
import sys
import network
import time
import logging
import dht
import BlynkLib
import urequests
from BlynkTimer import BlynkTimer
from machine import Pin
import socket

import constant  #User defined constant module for delaring constants

# Relay Pin Mapping(V0-V7 in the below order)
relayD12 = Pin(12, Pin.OUT)
relayD13 = Pin(13, Pin.OUT)
relayD14 = Pin(14, Pin.OUT)
relayD15 = Pin(15, Pin.OUT)
relayD21 = Pin(21, Pin.OUT)
relayD23 = Pin(23, Pin.OUT)
relayD25 = Pin(25, Pin.OUT)
relayD26 = Pin(26, Pin.OUT)
connectBlynkLED = Pin(2, Pin.OUT)
dht11 = dht.DHT11(Pin(4, Pin.IN, Pin.PULL_UP))

#DECLARED VARIABLES
timeout = 0
T_VPIN = 3
H_VPIN = 4

openWeatherAPI = constant.OPENWEATHER_BASE_API_URL+"q="+constant.OPENWEATHER_CITYNAME+"&appid="+constant.OPENWEATHER_APPID
connectBlynkLED.value(0)

#Timer initialisation Events
DHTSensortimer = BlynkTimer()
OpenWeatherAPICall = BlynkTimer()

#Method to curent current timestamp for logging and debugging
def getTimeStamp():
    systime = time.localtime()
    tstamp = str(systime[0])+"-"+str(systime[1])+"-"+str(systime[2])+" "+str(systime[3])+":"+str(systime[4])+":"+str(systime[5])+" "
    return tstamp

#Method to get timestamp from WorldTime API
def getTimeFromAPI():
    timeResponse=urequests.get(constant.WORLDTIMEAPI_URL)
    if(timeResponse.status_code==200):
        timeData=timeResponse.json()
        dateTime=timeData['datetime']
        dateTime=dateTime.replace("T"," ")
        dateTime=dateTime.split(".",1)[0]+" "
        return dateTime
    else:
        log.error("Sent GET request to WorldTimeAPI. Returned response with status code: {}".format(timeResponse.status_code))
        return "**Time API Error**: "

def blinkLEDOnEvent():
    connectBlynkLED.value(0)
    time.sleep(0.1)
    connectBlynkLED.value(1)

#Logging parameters
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("JACOB SMART HOME LOG")
log.info(getTimeStamp()+"STARTING JACOB SMART HOME SCRIPT VERSION {}".format(constant.SCRIPT_VERSION))
log.info(getTimeStamp()+"Logging started")

wifi = network.WLAN(network.STA_IF)

#Restarting Wifi
wifi.active(False)
time.sleep(0.5)
wifi.active(True)

#Scanning wifi available networks nearby
networks = wifi.scan()
logAvailableNetworks = 'Available Networks: ',networks
log.info(logAvailableNetworks)

#Initialising connection to declared wifi network
wifi.connect(constant.WIFI_SSID, constant.WIFI_PSD)

#Starting timer to try connecting to network for 5 secs. If failed, then loop fails 
if not wifi.isconnected():
    log.info(" Please wait while ESP32 is connecting to wifi..")
    while(not wifi.isconnected() and timeout<5):
        5-timeout
        timeout = timeout+1
        time.sleep(1)
         

if wifi.isconnected():
    wifiConnectedLog = 'Connection successful:', wifi.ifconfig()
    log.info(wifiConnectedLog)

else:
    log.error(getTimeStamp()+"Wifi Error: Connection Times Out!!!")
    sys.exit()

log.info(getTimeStamp()+" Connecting to Blynk server...")
blynk = BlynkLib.Blynk(constant.BLYNK_AUTH)

# BLYNK CORE FUNCTIONS

@blynk.on("connected")
def blynk_connected(ping):
    status= ("Blynk Connection Successful - Ping:", ping, "ms")
    connectBlynkLED.value(1)
    log.info(status)
    log.info(getTimeStamp()+"Syncing values for virtual pins from server...")
    blynk.sync_virtual(0,1,2,3,4,5,6,7)
    log.info(getTimeStamp()+"Syncing successful")
    try:
        pi_request=''
        ping_json = {'ping_value':ping}
        pi_request=urequests.get(constant.PI_LOCAL_SERVER_URL+'/blynk-connection',
        json=ping_json,
        headers=constant.REQUEST_HEADERS)
        log.info('Request to PI WEbServer send')
    except Exception as e:
        log.error('socket timed out')
    else:
        pi_request.close()
        log.info('Access successful.')
    
    
@blynk.on("disconnected")
def blynk_disconnected():
    connectBlynkLED.value(0)
    log.critical(getTimeStamp()+"Blynk disconnected")
    blynk.virtual_write(14, getTimeFromAPI()+"Blynk disconnected")
    try:
        pi_dis_request=''
        pi_dis_request=urequests.get(constant.PI_LOCAL_SERVER_URL+'/blynkDisconnect',headers=constant.REQUEST_HEADERS)
        pi_dis_request.close()
        log.info('Request to PI WEbServer send')
    except:
        log.critical("Unable to communicate with Raspberry PI server. Please check this on priority")

@blynk.on("V*")
def blynk_handle_vpins(pin, value):
    if(pin=="0"):
        if(int(value[0])==0):
            relayD12.value(1)
            log_message = constant.RELAYSTATEMSG.format(pin,12,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
        else:
            relayD12.value(0)
            log_message = constant.RELAYSTATEMSG.format(pin,12,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
    if(pin=="1"):
        if(int(value[0])==0):
            relayD13.value(1)
            log_message = constant.RELAYSTATEMSG.format(pin,13,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
        else:
            relayD13.value(0)
            log_message = constant.RELAYSTATEMSG.format(pin,13,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
    if(pin=="2"):
        if(int(value[0])==0):
            relayD14.value(1)
            log_message = constant.RELAYSTATEMSG.format(pin,14,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
        else:
            relayD14.value(0)
            log_message = constant.RELAYSTATEMSG.format(pin,14,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
    if(pin=="3"):
        if(int(value[0])==0):
            relayD15.value(1)
            log_message = constant.RELAYSTATEMSG.format(pin,15,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
        else:
            relayD15.value(0)
            log_message = constant.RELAYSTATEMSG.format(pin,15,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
    if(pin=="4"):
        if(int(value[0])==0):
            relayD21.value(1)
            log_message = constant.RELAYSTATEMSG.format(pin,21,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
        else:
            relayD21.value(0)
            log_message = constant.RELAYSTATEMSG.format(pin,21,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
    if(pin=="5"):
        if(int(value[0])==0):
            relayD23.value(1)
            log_message = constant.RELAYSTATEMSG.format(pin,23,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
        else:
            relayD23.value(0)
            log_message = constant.RELAYSTATEMSG.format(pin,23,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
    if(pin=="6"):
        if(int(value[0])==0):
            relayD25.value(1)
            log_message = constant.RELAYSTATEMSG.format(pin,25,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
        else:
            relayD25.value(0)
            log_message = constant.RELAYSTATEMSG.format(pin,25,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
    if(pin=="7"):
        if(int(value[0])==0):
            relayD26.value(1)
            log_message = constant.RELAYSTATEMSG.format(pin,26,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
        else:
            relayD26.value(0)
            log_message = constant.RELAYSTATEMSG.format(pin,26,int(value[0]))
            log.info(getTimeStamp()+log_message)
            blynk.virtual_write(14, getTimeFromAPI()+log_message)
    blinkLEDOnEvent()
    try:
        pin_request=''
        pin_json = {'pin':pin,'value':value}
        pin_request=urequests.get(constant.PI_LOCAL_SERVER_URL+'/updateRelayStatus',
        json=pin_json,
        headers=constant.REQUEST_HEADERS)
        pin_request.close()
        log.info('Request to PI WEbServer send')
    except:
        log.critical("Unable to communicate with Raspberry PI server. Please check this on priority")
    
    
def checkDHTSensorData():
    temperature = 0
    humidity = 0
    try:
        dht11.measure()
        temperature = dht11.temperature()
        humidity = dht11.humidity()
        log.info(getTimeStamp()+"Sending DHT11 sensor readings : Temperature={} Humidity={} to Blynk".format(temperature,humidity))
        blynk.virtual_write(14, getTimeFromAPI()+"Sending DHT11 sensor readings : Temperature={} Humidity={} to Blynk".format(temperature,humidity))
        try:
            pi_temp = ''
            temp_json = {'temp':temperature,'hum':humidity}
            pi_temp = urequests.get(constant.PI_LOCAL_SERVER_URL+'/updateDHTSuccess',json=temp_json,headers=constant.REQUEST_HEADERS)
            log.info('Request to PI WebServer send')
        except:
            log.critical('Unable to communicate with Raspberry PI server. Please check this on priority')
        else:
            pi_temp.close()    
        if(temperature>40):
            request=''
            sensor_json = {'value1':temperature, 'value2':humidity}
            request = urequests.post(
            constant.IFTT_BASE_URL + constant.EMAIL_API_KEY,
            json=sensor_json,
            headers=constant.REQUEST_HEADERS)
            if(request.status_code==200):
                log.info(getTimeStamp()+"High Room Temperature from DHT11 Detected. Trigerred IFTT Email Event successfully")
                blynk.virtual_write(14, getTimeFromAPI()+"High Room Temperature from DHT11 Detected. Trigerred IFTT Email Event successfully")
                try:
                    pi_email_temp = ''
                    pi_email_temp = urequests.get(constant.PI_LOCAL_SERVER_URL+'/highTempEmailSuccess',headers=constant.REQUEST_HEADERS)
                    pi_email_temp.close()
                    log.info('Request to PI WebServer send')
                except:
                    log.critical('Unable to communicate with Raspberry PI server. Please check this on priority')
            else:
                log.error(getTimeStamp+"IFTT Email API call failed. Request returned with status code: "+str(request.status_code)+". Please verify URL parameters in constant.py")
                blynk.virtual_write(14, getTimeFromAPI()+"IFTT Email API call failed. Request returned with status code: "+str(request.status_code)+". Please verify URL parameters in constant.py")
                try:
                    pi_email_temp = ''
                    error_json = {'error':str(request.status_code)}
                    pi_email_temp = urequests.get(constant.PI_LOCAL_SERVER_URL+'/highTempEmailFail',json=error_json,headers=constant.REQUEST_HEADERS)
                    log.info('Request to PI WebServer send')
                except:
                    log.critical('Unable to communicate with Raspberry PI server. Please check this on priority')
                else:
                    pi_email_temp.close()
            request.close()        
        
    except OSError as o_err:
        logErrorDHT = "Unable to get DHT11 sensor data: '{}'".format(o_err)
        log.error(getTimeStamp()+logErrorDHT)
        blynk.virtual_write(14, getTimeFromAPI()+logErrorDHT)
        try:
            pi_error_temp = ''
            temp_json={'error':o_err}
            pi_error_temp = urequests.get(constant.PI_LOCAL_SERVER_URL+'/updateDHTFail',json=temp_json,headers=constant.REQUEST_HEADERS)
            log.info('Request to PI WebServer send')
        except:
            log.critical('Unable to communicate with Raspberry PI server. Please check this on priority')
        else:
            pi_error_temp.close()

    blynk.virtual_write(8, temperature)
    blynk.virtual_write(9, humidity)
    
def checkOpenWeatherAPI():
    getTimeFromAPI()
    response=''
    response=urequests.get(openWeatherAPI)
    if(response.status_code==200):
        weatherData=response.json()
        tempHumPre=weatherData['main']
        openWeatherTemp=round(tempHumPre['temp'])-273.15
        openWeatherHum=tempHumPre['humidity']
        openWeatherPre=tempHumPre['pressure']*0.001
        openWeatherReport=weatherData['weather'][0]['description']
        openWeatherReport = openWeatherReport[0].upper() + openWeatherReport[1:]
        blynk.virtual_write(10,openWeatherTemp)
        blynk.virtual_write(11,openWeatherHum)
        blynk.virtual_write(12,openWeatherReport)
        blynk.virtual_write(13,openWeatherPre)
        log.info(getTimeStamp()+"OpenWeather API call successful. Sending response to Blynk. Temperature={} Humidity={} Report={} Pressure={}".format(str(openWeatherTemp),str(openWeatherHum),openWeatherReport,str(openWeatherPre)))
        blynk.virtual_write(14, getTimeFromAPI()+"OpenWeather API call successful. Sending response to Blynk. Temperature={} Humidity={} Report={} Pressure={}".format(str(openWeatherTemp),str(openWeatherHum),openWeatherReport,str(openWeatherPre)))
        weather_json = {'temp':openWeatherTemp , 'hum':openWeatherHum , 'report':openWeatherReport , 'pressure':openWeatherPre}
        try:
            pi_weather = ''
            pi_weather = urequests.get(constant.PI_LOCAL_SERVER_URL+'/updateWeatherSuccess',json=weather_json,headers=constant.REQUEST_HEADERS)
            log.info('Request to PI WebServer send')
        except:
            log.critical('Unable to communicate with Raspberry PI server. Please check this on priority')
        else:
            pi_weather.close()
        
    else:
        log.error(getTimeStamp()+"OpenWeather API call failed. Request returned status code:"+str(response.status_code)+". Please verify URL parameters in constant.py")
        blynk.virtual_write(14, getTimeFromAPI()+"OpenWeather API call failed. Request returned status code:"+str(response.status_code)+". Please verify URL parameters in constant.py")
        try:
            pi_weather = ''
            status_code_json={'code':str(response.status_code)}
            pi_weather = urequests.get(constant.PI_LOCAL_SERVER_URL+'/updateWeatherFail',json=status_code_json,headers=constant.REQUEST_HEADERS)
            log.info('Request to PI WebServer send')
        except:
            log.critical('Unable to communicate with Raspberry PI server. Please check this on priority')
        else:
            pi_weather.close()             
    response.close()

#Timers set as below
DHTSensortimer.set_interval(1800, checkDHTSensorData)
OpenWeatherAPICall.set_interval(2700, checkOpenWeatherAPI)

while True:
    blynk.run()
    DHTSensortimer.run()
    OpenWeatherAPICall.run()
