import zmq
import numpy as np
import time
import uhd

# context = zmq.Context()
# socket = context.socket(zmq.SUB)
# socket.connect("tcp://127.0.0.1:5555")
# socket.setsockopt_string(zmq.SUBSCRIBE, "")

# while True:
#     data = socket.recv()
#     print(len(data))
#     # print(data)
#     # break

max_size_frame_nsamps = 1024

devname = "X410"
if(devname == "N210"):
    # use GRC program instead. 
    pass
elif(devname == "N310"):
    samp_rate = 12.5e6
    # rx_freq = 1145.14e6
    rx_freq = 2355e6-2.5e6
    # rx_lo_offset = -50e6
    rx_lo_offset = 0e6
    gain = 50
    usrp_addr = "192.168.10.2"
    usrp_MClock = 125e6
elif(devname == "X410"):
    samp_rate = 6.25e6
    # rx_freq = 1145.14e6
    rx_freq = 2355e6
    # rx_lo_offset = -50e6
    rx_lo_offset = 0e6
    gain = 25.7
    usrp_addr = "192.168.10.5"
    usrp_MClock = 250e6
    pass
else:
    raise("Invalid device name!")

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://0.0.0.0:1145")

# usrp = uhd.usrp.MultiUSRP("addr=192.168.30.4, master_clock_rate=250e6") # X410
usrp = uhd.usrp.MultiUSRP(f"addr={usrp_addr}, master_clock_rate={usrp_MClock}") 
usrp.set_rx_freq(uhd.types.TuneRequest(rx_freq, rx_lo_offset), 0)
usrp.set_rx_rate(samp_rate, 0)
usrp.set_rx_gain(gain, 0)
usrp.set_rx_antenna("TX/RX", 0)
st_args = uhd.usrp.StreamArgs("fc32", "sc16")
st_args.channels = [0]
metadata = uhd.types.RXMetadata()
streamer = usrp.get_rx_stream(st_args)
buffer_samps = min(streamer.get_max_num_samps(), max_size_frame_nsamps)
recv_buffer = np.zeros((1, buffer_samps), dtype=np.complex64)
print("buffer size:", buffer_samps)
stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
stream_cmd.stream_now = True
streamer.issue_stream_cmd(stream_cmd)
while True:
    nsamps_received = streamer.recv(recv_buffer, metadata)
    if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
        print(metadata.strerror())
    if nsamps_received: 
        # print(nsamps_received)
        socket.send(recv_buffer[0, :nsamps_received].tobytes())
    #     time.sleep(size_frame_nsamps/samp_rate)
    #     # print(data)
    #     # break

    