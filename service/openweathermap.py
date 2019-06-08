### service/openweathermap: retrieve weather information from OpenWeatherMap
## HOW IT WORKS: 
## DEPENDENCIES:
# OS: 
# Python: 
## CONFIGURATION:
# required: api_key
# optional: 
## COMMUNICATION:
# INBOUND: 
# - IN: 
#   required: request ("temperature", "pressure", "humidity", "wind", "condition", "description"), latitude, longitude
#   optional: 
# OUTBOUND: 

import json
import datetime
import time
 
from sdk.python.module.service import Service
from sdk.python.utils.datetimeutils import DateTimeUtils

import sdk.python.utils.web
import sdk.python.utils.numbers
import sdk.python.utils.exceptions as exception

class Openweathermap(Service):
   # What to do when initializing
    def on_init(self):
        # constants
        self.url = 'http://api.openweathermap.org/data/2.5/'
        # configuration file
        self.config = {}
        # helpers
        self.date = None
        self.units = None
        self.language = None
        # require configuration before starting up
        self.add_configuration_listener("house", True)
        self.add_configuration_listener(self.fullname, True)

    # map between user requests and openweathermap requests
    def get_request_type(self,request):
        if request in ["temperature", "pressure", "humidity", "wind", "condition", "description"]: return "weather"
        return None
    
    # What to do when running    
    def on_start(self):
        pass
    
    # What to do when shutting down
    def on_stop(self):
        pass

    # What to do when receiving a request for this module
    def on_message(self, message):
        if message.command == "IN":
            if not self.is_valid_configuration(["request", "latitude", "longitude"], message.get_data()): return
            sensor_id = message.args
            request = message.get("request")
            location = "lat="+str(message.get("latitude"))+"&lon="+str(message.get("longitude"))
            if self.get_request_type(request) is None:
                self.log_error("invalid request "+request)
                return
            # if the raw data is cached, take it from there, otherwise request the data and cache it
            cache_key = "/".join([location, self.get_request_type(request)])
            if self.cache.find(cache_key): 
                data = self.cache.get(cache_key)
            else:
                url = self.url+"/"+self.get_request_type(request)+"?APPID="+self.config["api_key"]+"&units="+self.units+"&lang="+self.language+"&"+location
                try:
                    data = sdk.python.utils.web.get(url)
                except Exception,e: 
                    self.log_error("unable to connect to "+url+": "+exception.get(e))
                    return
                self.cache.add(cache_key,data)
            # parse the raw data
            try: 
                parsed_json = json.loads(data)
            except Exception,e: 
                self.log_error("invalid JSON returned")
                return
            if not "cod" in parsed_json:
                self.log_error("JSON missing 'cod': "+str(parsed_json))
                return
            if parsed_json["cod"] != 200:
                self.log_error(parsed_json["message"])
                return
            # reply to the requesting module 
            message.reply()
            # handle the request
            if request == "temperature":
                message.set("value", float(parsed_json["main"]["temp"]))
                message.set("timestamp", self.date.timezone(int(parsed_json["dt"])))
            elif request == "humidity":
                message.set("value", float(parsed_json["main"]["humidity"]))
                message.set("timestamp", self.date.timezone(int(parsed_json["dt"])))
            elif request == "wind":
                message.set("value", float(parsed_json["wind"]["speed"]))
                message.set("timestamp", self.date.timezone(int(parsed_json["dt"])))
            elif request == "pressure":
                message.set("value", float(parsed_json["main"]["pressure"]))
                message.set("timestamp", self.date.timezone(int(parsed_json["dt"])))
            elif request == "condition":
                code = parsed_json["weather"][0]["main"]
                value = "question"
                if code in ["Thunderstorm"]: value = "cloud-showers-heavy"
                elif code in ["Drizzle", "Mist", "Smoke", "Haze", "Dust", "Fog", "Sand", "Ash", "Squall", "Tornado"]: value = "smog"
                elif code in ["Rain"]: value = "cloud-rain"
                elif code in ["Snow"]: value = "snowflake"
                elif code in ["Clear"]: value = "sun"
                elif code in ["Clouds"]: value = "cloud"
                message.set("value", value)
                message.set("timestamp", self.date.timezone(int(parsed_json["dt"])))
            elif request == "description":
                message.set("value", parsed_json["weather"][0]["description"])
                message.set("timestamp", self.date.timezone(int(parsed_json["dt"])))
            # TODO: add other capabilities
            # send the response back
            self.send(message)

    # What to do when receiving a new/updated configuration for this module
    def on_configuration(self,message):
        # we need house timezone
        if message.args == "house":
            if not self.is_valid_module_configuration(["timezone", "units", "language"], message.get_data()): return False
            self.date = DateTimeUtils(message.get("timezone"))
            self.units = message.get("units")
            self.language = message.get("language")
        # module's configuration
        if message.args == self.fullname:
            if not self.is_valid_module_configuration(["api_key"], message.get_data()): return False
            self.config = message.get_data()
