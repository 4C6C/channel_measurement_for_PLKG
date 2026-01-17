# By GuJi 2025.12
import zmq
import numpy as np
import time
import uhd
# import matplotlib.pyplot as plt

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
samp_rate = 12.5e6
# rx_freq = 1145.14e6
tx_freq = 2100e6
tx_lo_offset = 0e6
gain = 31

# context = zmq.Context()
# socket = context.socket(zmq.PULL)
# socket.connect("tcp://127.0.0.1:1146")

usrp = uhd.usrp.MultiUSRP("addr=192.168.10.2")
# usrp.set_tx_freq(tx_freq)
usrp.set_tx_freq(uhd.types.TuneRequest(tx_freq, tx_lo_offset), 0)
usrp.set_tx_gain(gain, 0)
usrp.set_tx_rate(samp_rate, 0)
usrp.set_tx_antenna("TX/RX", 0)
# print("[USRP Tuning] Actual TX LO Freq:", usrp.get_tx_lo_freq("rfic", 0))
st_args = uhd.usrp.StreamArgs("fc32", "sc16")
st_args.channels = [0]
metadata = uhd.types.TXMetadata()
streamer = usrp.get_tx_stream(st_args)
buffer_samps = min(streamer.get_max_num_samps(), max_size_frame_nsamps)
# send_buffer = np.zeros((1, buffer_samps), dtype=np.complex64)
print("buffer size:", buffer_samps)
tx_buffer = np.zeros((1, buffer_samps), dtype=np.complex64)
tx_buffer[0, :] = 0.92
# buffer_bytes = buffer_samps*4
tx_md = uhd.types.TXMetadata()
tx_md.start_of_burst = True
tx_md.end_of_burst = False
tx_md.has_time_spec = False
while True:
    streamer.send(tx_buffer, tx_md)
    tx_md.start_of_burst = False
    # data = socket.recv(copy=True)
    # l_data = len(data)
    # if(l_data%4 != 0):
    #     print("Error! Data unaligned. ")
    # print(len(data))
    # data1 = np.frombuffer(data, dtype=np.int16)
    # data2 = np.reshape(data1, [-1, 2], 'C')
    # # print(data2)
    # plt.plot(data2[:, 0])
    # plt.plot(data2[:, 1])
    # plt.show()
    # p_data = 0
    # print("\n", l_data)
    # while True:
    #     if(p_data + buffer_bytes > l_data):
    #         ndata_tx = l_data-p_data
    #     else:
    #         ndata_tx = buffer_bytes
    #     # print(ndata_tx, end=" ")
    #     # print(data[p_data:p_data+buffer_bytes])
    #     streamer.send(np.frombuffer(data[p_data:p_data+buffer_bytes], dtype=np.int32), tx_md)
    #     tx_md.start_of_burst = False
    #     p_data += ndata_tx
    #     if(p_data == l_data):
    #         break
    # nsamps_received = streamer.recv(recv_buffer, metadata)
    # if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
    #     print(metadata.strerror())
    # if nsamps_received:
    #     # print(nsamps_received)
    #     socket.send(recv_buffer[:nsamps_received].tobytes())
    # #     time.sleep(size_frame_nsamps/samp_rate)
    #     # print(data)
    #     # break

    