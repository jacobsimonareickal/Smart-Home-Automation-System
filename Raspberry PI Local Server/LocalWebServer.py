import RPi.GPIO as GPIO
import os
import json
import config
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

 #Method to get timestamp from WorldTime API
def getTimeFromAPI():
    timeResponse=requests.get(config.WORLDTIMEAPI_URL)
    if(timeResponse.status_code==200):
        timeData=timeResponse.json()
        dateTime=timeData['datetime']
        dateTime=dateTime.replace("T"," ")
        dateTime=dateTime.split(".",1)[0]+" "
        return dateTime
    else:
        return "**Time API Error**: "

class MyServer(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        if(self.path=='/blynk-connection'):
            content_length = int(self.headers['content-length'])
            body = self.rfile.read(content_length)
            result = json.loads(body)
            ping = result['ping_value']
            self.do_HEAD()
            f=open(config.ESP32LOG_FILE_NAME,"a")
            f.write(getTimeFromAPI()+"ESP32 connected to Blynk with ping:"+str(ping)+"\n")
            f.close()
        if(self.path=='/highTempEmailSuccess'):
            self.do_HEAD()
            f=open(config.ESP32LOG_FILE_NAME,"a")
            f.write(getTimeFromAPI()+"ESP32 has triggered a successful IFTT email event due to high temperature detection."+"\n")
            f.close()
        if(self.path=='/blynkDisconnect'):
            self.do_HEAD()
            f=open(config.ESP32LOG_FILE_NAME,"a")
            f.write(getTimeFromAPI()+"Critical: ESP32 has disconnected from blynk. Please check on priority"+"\n")
            f.close()
        if(self.path=='/highTempEmailFail'):
            content_length = int(self.headers['content-length'])
            body = self.rfile.read(content_length)
            result = json.loads(body)
            error = result['error']
            self.do_HEAD()
            f=open(config.ESP32LOG_FILE_NAME,"a")
            f.write(getTimeFromAPI()+"ESP32 has attempted to trigger an IFTT mail event but event has failed with status code: {} Due to this email has not been send".format(error)+"\n")
            f.close()
        if(self.path=='/updateWeatherFail'):
            content_length = int(self.headers['content-length'])
            body = self.rfile.read(content_length)
            result = json.loads(body)
            status_code = result['code']
            self.do_HEAD()
            f=open(config.ESP32LOG_FILE_NAME,"a")
            f.write(getTimeFromAPI()+"ESP32 received error response code {} when trying to connect with OpenWeatherAPI. Blynk may not have the latest weather data due to this.".format(status_code)+"\n")
            f.close()
        if(self.path=='/updateDHTSuccess'):
            content_length = int(self.headers['content-length'])
            body = self.rfile.read(content_length)
            result = json.loads(body)
            temp = result['temp']
            hum = result['hum']
            self.do_HEAD()
            f=open(config.ESP32LOG_FILE_NAME,"a")
            f.write(getTimeFromAPI()+"ESP32 received sensor readings from DHT11 and updated the sensor data to Blynk. (Temperature: {} Humidity: {})".format(temp,hum)+"\n")
            f.close()
        if(self.path=='/updateDHTFail'):
            content_length = int(self.headers['content-length'])
            body = self.rfile.read(content_length)
            result = json.loads(body)
            error = result['error']
            self.do_HEAD()
            f=open(config.ESP32LOG_FILE_NAME,"a")
            f.write(getTimeFromAPI()+"ESP32 could not read DHT11 sensor. Sensor returned error: {} Please check connection or if the sensor is faulty".format(error)+"\n")
            f.close()
        if (self.path=="/updateWeatherSuccess"):
            content_length = int(self.headers['content-length'])
            body = self.rfile.read(content_length)
            result = json.loads(body)
            temp = result['temp']
            hum = result['hum']
            report = result['report']
            pressure = result['pressure']
            f=open(config.ESP32LOG_FILE_NAME,"a")
            f.write(getTimeFromAPI()+"ESP32 received weather data from OpenWeather API and send data to Blynk cloud (Temperature = {} Humidity = {} Report = {} Pressure = {}".format(temp,hum,report,pressure)+"\n")
            f.close()
            
        if (self.path=='/updateRelayStatus'):
            content_length = int(self.headers['content-length'])
            body = self.rfile.read(content_length)
            result = json.loads(body)
            pin = result['pin']
            value = result['value']
            f=open(config.ESP32LOG_FILE_NAME,"a")
            if (pin == '0'):
                f.write(getTimeFromAPI()+config.RELAYSTATEMSG.format(pin,12,value)+"\n")
            if (pin == '1'):
                f.write(getTimeFromAPI()+config.RELAYSTATEMSG.format(pin,13,value)+"\n")
            if (pin == '2'):
                f.write(getTimeFromAPI()+config.RELAYSTATEMSG.format(pin,14,value)+"\n")
            if (pin == '3'):
                f.write(getTimeFromAPI()+config.RELAYSTATEMSG.format(pin,15,value)+"\n")
            if (pin == '4'):
                f.write(getTimeFromAPI()+config.RELAYSTATEMSG.format(pin,21,value)+"\n")
            if (pin == '5'):
                f.write(getTimeFromAPI()+config.RELAYSTATEMSG.format(pin,23,value)+"\n")
            if (pin == '6'):
                f.write(getTimeFromAPI()+config.RELAYSTATEMSG.format(pin,25,value)+"\n")
            if (pin == '7'):
                f.write(getTimeFromAPI()+config.RELAYSTATEMSG.format(pin,26,value)+"\n")
            f.close()
            self.do_HEAD()
            
        else:
            html = '''
               <html>
               <body
               style="width:960px; margin: 20px auto;">
               <h1><center>Raspberry Pi Local Web Server Version {}<center></h1>
               <h1><center>(Developed by Jacob)<center></h1>
               <p style="color:green">PI Server Status: Online</p>
               <p>Raspberry PI Local Web Server IP Address: {}</p>
               <p>Raspberry PI Local Web Server IP Port   : {}</p>
               </body>
               </html>
            '''
            self.do_HEAD()
            self.wfile.write(html.format(config.WEB_SERVER_VERSION,config.HOST_NAME,config.HOST_PORT).encode("utf-8"))

    def do_POST(self):
        print('here')


# # # # # Main # # # # #

if __name__ == '__main__':
    http_server = HTTPServer((config.HOST_NAME, config.HOST_PORT), MyServer)
    print("Server Starts - %s:%s" % (config.HOST_NAME, config.HOST_PORT))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
