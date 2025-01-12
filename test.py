routers = {"R1": "192.168.15.150", 
               "R2": "192.168.15.151", 
               "R3": "192.168.15.152"
               }

for router, ip_address in routers.items():
    print("key " + router + " IP " + ip_address)

