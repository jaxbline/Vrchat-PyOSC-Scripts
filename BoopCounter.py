import socket, time, re, asyncio, pickle
from pythonosc import udp_client

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 9001))

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

db_file = 'BoopsCounted.pickle'

try:
    with open(db_file, 'rb') as f:
        boops = pickle.load(f)
except FileNotFoundError:
    boops = 0
    print("Creating new save file for boops count...")

print("Starting Boop Counter!")

last_called_time = 0
call_count = 0

async def noseboops():
    global last_called_time, call_count, boops
    current_time = time.time()
    if current_time - last_called_time < 2:
        call_count += 1
        return
    last_called_time = current_time
    boops += call_count
    print(f"boops: {boops}")
    client.send_message("/chatbox/input", [f"Boops : {boops} ", True])
    with open(db_file, 'wb') as f:
        pickle.dump(boops, f)
    call_count = 0
    await asyncio.sleep(1)

async def main():
    while True:
        data, address = sock.recvfrom(1024)
        output = data.decode('latin-1').replace("b'avatarparameters", "")
        output = re.sub(r'[^a-zA-Z0-9\s]', '', output)

        if "BoopCount" in output:
            await noseboops()

try:
    asyncio.run(main())
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Closing the Boop Counter")
