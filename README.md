# meross_to_mqtt
Simple Python script to publish out MQTT message when Meross sockets change state

This uses the excellent [MerossIot](https://github.com/albertogeniola/MerossIot) Python plugin and some async Paho MQTT to intercept Meross device events and republish them as simple MQTT.  It is coded to support the devices I use (UK single and multi sockets that are paired directly with HomeKit) but could be extended / adjusted as needed.  I am using this to get the state of HomeKit Meross sockets for a custom IHD. 

Hopefully this maybe useful for other peoples projects or a starting point for something wider. 
