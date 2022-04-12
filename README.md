Smart-Home-Automation-System
A smart home automation system using ESP32 and Raspberry PI developed in Micropython and Python 3  

Project Name        - Home Automation Using ESP32 and Micropython  
Project Author      - Jacob Simon Areickal  
Project Version     - 1.0.0  
Project Description - A basic home automation project using ESP32 and micropython. This project lets you control multiple relays from cloud and will also display temperature and humidity using DHT22 sensor  
Project Code Core Module Changes  
   1. 22-Mar-2022 - Added Email Functionality For High Temperature Reading  
   2. 22-Mar-2022 - Added timestamp functionality for logging and debugging  
   3. 24-Mar-2022 - Added live weather functionality using OpenWeather API  
   4. 25-Mar-2022 - Changed relay switching logic for easy debugging and reduced time complexity  
   5. 25-Mar-2022 - Added functionality which sends GET to WorlTimeAPI to return current local time. ESP32 will still be able to get local time even when not connected to PC due to this addition.  
   6. 26-Mar-2022 - Added an LED blink function for the on board LED to notify when ESP is connected and Blynk and registering Blynk events    

Defects detected and needed to be worked on:  
     1. Unable to handle https requests. ESP32 returns out of memory error when requests are made using https  
     2. Need to fix project source code's time complexity and make it more memory efficient.  
     3. Need to implement more exception handling to handle exceptions during runtime.  

ESP32 microcontroller talks to a Raspberry PI Web server for handling logging and complex operaions.Since Raspberry PI runs on a full version of Python istead of micropython, the possibilities that can be achived is limitless.  

 Make sure you give your parameters in config.py and constatnt.py  

