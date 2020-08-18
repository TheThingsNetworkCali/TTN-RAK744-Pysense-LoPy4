import time
import binascii
import socket
import ujson
import pycom
from network import LoRa
from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

# Turn off led
pycom.heartbeat(False)

# ------------------ JOIN TO LORA NETWORK --------------------------------------

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915)

with open("secrets.json") as fp:
    secrets = ujson.load(fp)
    app_eui = binascii.unhexlify(secrets["app_eui"])
    app_key = binascii.unhexlify(secrets["app_key"])

lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print("Not joined yet...")

print('Network joined!')

# ------------------ END JOIN TO LORA NETWORK --------------------------------------


s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 1)
s.setblocking(False)

while True:
    # ----------------------- GET PYSENSE DATA -------------------------------------
    data = {}

    py = Pysense()
    si = SI7006A20(py)

    # Returns height in meters.
    mp = MPL3115A2(py,mode=ALTITUDE)

    # Returns pressure in Pascals
    mpp = MPL3115A2(py,mode=PRESSURE)

    # Channel Blue lux, channel Red lux
    lt = LTR329ALS01(py)

    #
    li = LIS2HH12(py)


    data["altitude"] = str(mp.altitude())
    # data["pressure"] = str(mpp.pressure())
    data["temperature"] = str(si.temperature()) # deg C
    # data["light"] = str(lt.light())
    # data["acceleration"] = str(li.acceleration())
    # data["roll"] = str(li.roll())
    # data["pitch"] = str(li.pitch())
    # data["battery_voltage"] = str(py.read_battery_voltage())
    # ----------------------- END PYSENSE DATA -------------------------------------

    to_send = bytes(str(data), "utf-8")

    print("to_send %s" % to_send)

    s.send(to_send)

    time.sleep(99)
