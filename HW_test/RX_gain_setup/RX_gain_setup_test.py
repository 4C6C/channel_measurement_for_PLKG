import zmq
import numpy as np
import time
import uhd
import matplotlib.pyplot as plt
import sys

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
devname = "N210"
if(devname == "N210"):
    # use GRC program instead. 
    samp_rate = 12.5e6
    # rx_freq = 1145.14e6
    rx_freq = 2100e6
    # rx_lo_offset = -50e6
    rx_lo_offset = -10e6
    gain = 16
    usrp_addr = "192.168.10.2"
    usrp_MClock = 100e6
elif(devname == "N310"):
    samp_rate = 12.5e6
    # rx_freq = 1145.14e6
    rx_freq = 2355e6-2.5e6
    # rx_lo_offset = -50e6
    rx_lo_offset = 0e6
    gain = 50
    usrp_addr = "192.168.30.2"
    usrp_MClock = 125e6
elif(devname == "X410"):
    samp_rate = 6.25e6
    # rx_freq = 1145.14e6
    rx_freq = 2355e6
    # rx_lo_offset = -50e6
    rx_lo_offset = 0e6
    gain = 22.5
    usrp_addr = "192.168.30.4"
    usrp_MClock = 250e6
    pass
else:
    raise("Invalid device name!")

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

usrp.set_time_next_pps(uhd.types.TimeSpec(0))
time.sleep(2.2)
print("UHD Device time last PPS:  ", usrp.get_time_last_pps().get_real_secs())
print("UHD Device time right now: ", usrp.get_time_now().get_real_secs())

n_trials = 100
i_trials = 0
rx_record_len = int(0.1*samp_rate)
current_settings_iq_envelope_max = np.zeros(rx_record_len+buffer_samps, dtype=np.float64)
current_settings_iq_envelope_min = np.zeros(rx_record_len+buffer_samps, dtype=np.float64)
current_settings_iq_envelope_avg = np.zeros(rx_record_len+buffer_samps, dtype=np.float64)
recording_triggered = False
recording_pos = 0
nticks_to_setup_gain_init = 0.1*samp_rate
nticks_to_setup_gain = nticks_to_setup_gain_init


stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
stream_cmd.stream_now = True
streamer.issue_stream_cmd(stream_cmd)
while True:
    nsamps_received = streamer.recv(recv_buffer, metadata)
    if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
        print(metadata.strerror())
    if nsamps_received:
        # print(nsamps_received)
        if(recording_triggered):
            if(i_trials == 0):
                current_settings_iq_envelope_max[recording_pos:recording_pos+nsamps_received] = np.abs(recv_buffer[0, :nsamps_received])
                current_settings_iq_envelope_min[recording_pos:recording_pos+nsamps_received] = np.abs(recv_buffer[0, :nsamps_received])
                current_settings_iq_envelope_avg[recording_pos:recording_pos+nsamps_received] = np.abs(recv_buffer[0, :nsamps_received])
            else:
                current_settings_iq_envelope_max[recording_pos:recording_pos+nsamps_received] = np.maximum(np.abs(recv_buffer[0, :nsamps_received]), current_settings_iq_envelope_max[recording_pos:recording_pos+nsamps_received])
                current_settings_iq_envelope_min[recording_pos:recording_pos+nsamps_received] = np.minimum(np.abs(recv_buffer[0, :nsamps_received]), current_settings_iq_envelope_min[recording_pos:recording_pos+nsamps_received])
                current_settings_iq_envelope_avg[recording_pos:recording_pos+nsamps_received] = np.abs(recv_buffer[0, :nsamps_received]) + current_settings_iq_envelope_avg[recording_pos:recording_pos+nsamps_received]
            recording_pos += nsamps_received
            if(recording_pos >= rx_record_len):
                # one trial is completed
                i_trials += 1
                print(i_trials)
                if(i_trials >= n_trials):
                    break
                else:
                    # reset gain, prepare for the next trigger
                    nticks_to_setup_gain = nticks_to_setup_gain_init
                    recording_triggered = False
                    usrp.set_rx_gain(gain-1, 0)
        else:
            nticks_to_setup_gain -= nsamps_received
            if(nticks_to_setup_gain <= 0):
                recording_triggered = True
                recording_pos = 0
                usrp.set_rx_gain(gain, 0)


stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
stream_cmd.stream_now = True
streamer.issue_stream_cmd(stream_cmd)


current_settings_iq_envelope_avg /= n_trials

dataname = f"result_RX_gain_setup_{devname}"
np.savetxt(f"{dataname}_max.csv", current_settings_iq_envelope_max, delimiter=",")
np.savetxt(f"{dataname}_min.csv", current_settings_iq_envelope_min, delimiter=",")
np.savetxt(f"{dataname}_avg.csv", current_settings_iq_envelope_avg, delimiter=",")


plt.plot(current_settings_iq_envelope_min[:], label='min')
plt.plot(current_settings_iq_envelope_max[:], label='max')
plt.plot(current_settings_iq_envelope_avg[:], label='avg')
plt.legend()
plt.show()

