import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial.tools
import serial.tools.list_ports
import logging

ports = serial.tools.list_ports.comports()

if len(ports) == 1:
    port = ports[0]
else:
    raise RuntimeError("Too many ports - modify script to pick one")

logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)
baud_rate=115200

logger.info("Opening port %s/%s", port, port.name)

ser = serial.Serial(port.name, baudrate=baud_rate)
ser.flush()

# Initialize temperature array
temps = np.zeros(768)
max_temp = 0
min_temp = 500

min_range = 0
max_range = 500
# Create the figure for plotting
fig, ax = plt.subplots()
heatmap = ax.imshow(
    np.zeros((24, 32)), 
    cmap='hsv' , 
    vmin=min_range, 
    vmax=max_range,
    interpolation="bilinear",
    origin="upper"
    )
ax.invert_xaxis()
max = ax.annotate("max:", (0,0))
min = ax.annotate("min:", (0,0))
#plt.colorbar(heatmap)
START_FLAG = 0x5A

def read_serial_data():
    global max_temp, min_temp
    find_frame_flag = False

    # keep reading until the START_FLAG is observed twice (0x5a5a)
    if not find_frame_flag:
        data = 0
        flag_count = 0
        while 1:
            data = ser.read()
            if int.from_bytes(data, 'little') == START_FLAG:
                flag_count +=1 
                if flag_count == 2:
                    find_frame_flag = True
                    logger.info("Found start flag bytes")
                    break
            else:
                flag_count = 0
    
    find_frame_flag = False
    
    data = ser.read(2)
    data_len = int.from_bytes(data[:2], "little")
    sum = START_FLAG * 256 + START_FLAG + data_len

    logger.info("Frame length: %x", data_len)
    data = ser.read(data_len -2)

    # Update min and max temperatures
    max_temp = 0
    min_temp = 500


    for q in range(data_len // 2 -1):
        value = int.from_bytes(data[q*2:q*2+2], "little")
        sum += value
        value = value/100.0
        if value > max_temp:
            max_temp = value
        if value < min_temp:
            min_temp = value

    for q in range(data_len // 2 -1):
        value = int.from_bytes(data[q*2:q*2+2], "little") / 100
        mapped_value = np.clip(np.interp(value, [min_temp, max_temp], [min_range, max_range]), min_range, max_range)
        temps[q] = mapped_value
    data = ser.read(2)
    v = int.from_bytes(data, "little")

    sum += v

    data = ser.read(2)
    v = int.from_bytes(data, "little")

    parity_sum = v
    logger.info("Parity sum: %x %s", sum, parity_sum)


def update_heatmap(*args):
    read_serial_data()
    mat = temps.reshape((24,32))
    heatmap.set_array(mat)
    max_point = np.unravel_index(temps.argmax(), mat.shape[:2])
    max.set_position(max_point)
    max.set_text(str(max_temp) + "C")

    min_point = np.unravel_index(temps.argmin(), mat.shape[:2])
    min.set_position(min_point)
    min.set_text(str(min_temp) + "C")
    
    return heatmap,

REFRESH_RATE = 8

ani = animation.FuncAnimation(fig, update_heatmap, interval=1000/REFRESH_RATE, save_count=10)


plt.show()