import requests
import datetime


def get_current_ip():
    return requests.get("https://api64.ipify.org").text


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def beep():
    pass  # Silent - Linux compatible
    
def beeplow():
    pass  # Silent - Linux compatible
    
def beepshort():
    pass  # Silent - Linux compatible

def beeploww():
    pass  # Silent - Linux compatible