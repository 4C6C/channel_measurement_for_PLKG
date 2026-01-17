import zmq
import socket
import numpy as np
import time
import uhd
import matplotlib.pyplot as plt
import sys
# import struct

# context = zmq.Context()
# socket = context.socket(zmq.SUB)
# socket.connect("tcp://127.0.0.1:5555")
# socket.setsockopt_string(zmq.SUBSCRIBE, "")

# # Raw IQ Forwarding
# zmq_context = zmq.Context()
# zmq_socket = zmq_context.socket(zmq.PUB)
# zmq_socket.bind("tcp://0.0.0.0:1145")

# while True:
#     data = socket.recv()
#     print(len(data))
#     # print(data)
#     # break
# time.sleep(1)
samp_rate = 6.25e6
tx_lo_freq = 2355e6
# rx_lo_freq = tx_lo_freq
rx_lo_offset = -50e6
# tx_lo_offset = -50e6
tx_lo_offset = 0
rxgain = 25.7
txgain = 60
ueid = "B"
# if(len(sys.argv) < 2):
#     print("Invalid parameter! ")
#     exit()
# ueid = sys.argv[1]
timing_correction_for_uA = 0e-6
T_2way_measure = 200e-6 # 500us
T_txb = T_2way_measure / 2
# T_trx_gap = 50e-6 # T_trx_gap*samp_rate must be an integer
# if(ueid == "A"):
#     parity_tx = 0
#     usrp_addr = "192.168.10.2"
#     port_udpsock = 19198
#     timing_correction = timing_correction_for_uA
# elif(ueid == "B"):
parity_tx = 1
parity_tx = 0
usrp_addr = "192.168.30.4"
port_udpsock = 19199
timing_correction = 0
# else:
#     print("Invalid UEID!")
#     exit()
tx_timing_calibration_nsample = -50
t_tx_advance = 50e-3 + T_txb*parity_tx # TX slot control and compensate for the streaming delay
nticks_rxb = int(T_2way_measure*samp_rate)
nticks_txb = int(T_txb*samp_rate)
# nticks_trx_gap = int(T_trx_gap*samp_rate)
nticks_tx_advance = int(t_tx_advance*samp_rate)+tx_timing_calibration_nsample
digi_if_freq = 0.05
rx_lo_freq = tx_lo_freq - digi_if_freq * samp_rate
# freq_tolerance = 12.5e3
freq_tolerance = 500e3 # For new magnitude detection algorithm
# nfft = (nticks_txb-nticks_trx_gap*2)
# nfft_tolerance = int(round(freq_tolerance/(samp_rate/nfft)))
# if_fftpos = int(digi_if_freq*nfft)
len_pkt_nCSIs = 100 # number which CSI packets will be aligned to
# fft_window = np.blackman(nticks_txb-(nticks_trx_gap*2))
# print(fft_window.dtype, np.size(fft_window))
# plt.plot(fft_window)
# plt.show()
# exit()

# UDP Interface Here
udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpsock.bind(("0.0.0.0", port_udpsock))
# udpsock.setblocking(False)

usrp = uhd.usrp.MultiUSRP("addr="+usrp_addr+", clock_source=internal,time_source=internal, master_clock_rate=250e6")
# usrp = uhd.usrp.MultiUSRP("addr="+usrp_addr+", clock_source=external,time_source=external, master_clock_rate=125e6")
usrp.set_rx_freq(uhd.types.TuneRequest(rx_lo_freq, rx_lo_offset), 0)
usrp.set_rx_rate(samp_rate, 0)
usrp.set_rx_gain(rxgain, 0)
usrp.set_rx_antenna("TX/RX", 0)
usrp.set_tx_freq(uhd.types.TuneRequest(tx_lo_freq, tx_lo_offset), 0)
usrp.set_tx_rate(samp_rate, 0)
usrp.set_tx_gain(txgain, 0)

# Timing source: Internal
usrp.set_clock_source("internal")
usrp.set_time_source("internal")
# # Timing source: GPSDO
# usrp.set_clock_source("gpsdo")
# usrp.set_time_source("gpsdo")
# # Timing source: External
# usrp.set_clock_source("external")
# usrp.set_time_source("external")

# # Check for GPS lock
# gps_locked = usrp.get_mboard_sensor("gps_locked", 0)
# if(gps_locked.to_bool()):
#     print("GPS locked!")
# else:
#     print("GPS not locked! ")
#     # exit()
# print("Waiting for reference lock...")
# while(not usrp.get_mboard_sensor("ref_locked", 0).to_bool()):
#     time.sleep(0.5)
# print("Reference locked.")
# gps_time = usrp.get_mboard_sensor("gps_time")
# print("GPS Time:", gps_time.to_int())
# print("Time last PPS:", usrp.get_time_last_pps().to_ticks(1.0))
# usrp.set_time_next_pps(uhd.types.TimeSpec(gps_time.to_int() + 1.0 + timing_correction))
# # usrp.set_time_next_pps(uhd.types.TimeSpec(0))
# time.sleep(2.2)
# print("GPS Epoch time at last PPS:", usrp.get_mboard_sensor("gps_time").to_real())
# print("UHD Device time last PPS:  ", usrp.get_time_last_pps().get_real_secs())
# print("UHD Device time right now: ", usrp.get_time_now().get_real_secs())

# Set internal clock
usrp.set_time_next_pps(uhd.types.TimeSpec(0))
time.sleep(2.2)
print("UHD Device time last PPS:  ", usrp.get_time_last_pps().get_real_secs())
print("UHD Device time right now: ", usrp.get_time_now().get_real_secs())

tgt_size_buffer_nsamps = 2500 # 1250/5
st_args = uhd.usrp.StreamArgs("fc32", "sc16")
st_args.channels = [0]
rx_md = uhd.types.RXMetadata()
rxstreamer = usrp.get_rx_stream(st_args)
nsamps_buffer = min(rxstreamer.get_max_num_samps(), tgt_size_buffer_nsamps)
rx_buffer = np.zeros((1, nsamps_buffer), dtype=np.complex64)
rx_frame_buf = np.zeros((1, nticks_rxb), dtype=np.complex64)
# rx_frame_buf_LPF = np.zeros((1, nfft), dtype=np.complex64)
tx_buffer = np.zeros((1, nticks_txb), dtype=np.complex64)
txstreamer = usrp.get_tx_stream(st_args)
tx_md = uhd.types.TXMetadata()
# tx_md.start_of_burst = True
# tx_md.end_of_burst = True
# tx_md.has_time_spec = True
# tx_buffer[0, :] = 0.9*np.exp(2j*np.pi*digi_if_freq*np.arange(np.size(tx_buffer)))
# tx_buffer[0, :] = 0.9*np.exp(2j*np.pi*digi_if_freq*np.arange(np.size(tx_buffer)))
# tx_buffer[0, :] = 0.75
# tx_buffer[0, nticks_txb-50:] = 0
# tx_buffer[0, 100:] = 0 // For timing debugging only
mag_CSIs = np.zeros(len_pkt_nCSIs, dtype=np.float32)
print("RX buffer size:", nsamps_buffer)
stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
stream_cmd.stream_now = False
# print("Waiting for CSI Collecter...")
# while(True):
#     (msg, remoteaddr) = udpsock.recvfrom(1500)
#     if(msg == b"Start!"):
#         break
# print("CSI Collecter is online.")

# TRx Gap Parameter Scanning Specific

n_frames_per_set = 10000
iframes_in_current_set = 0
i_set = 0
# tx_gap_prefix_time = 100e-6
tx_gap_prefix_time = 0e-6
# tx_gap_postfix_times = list(np.arange(0, 50, 25)*1e-6)
# tx_gap_postfix_times = list(np.float64([0,10,20])*1e-6)
tx_gap_postfix_times = list(np.float64([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])*1e-6)
n_sets = len(tx_gap_postfix_times)
nframes_to_wait_init = int(round(t_tx_advance*samp_rate/nticks_rxb*2))
nframes_to_wait = 1000

tx_buffer[0, :] = 0
tx_buffer[0, int(round(tx_gap_prefix_time*samp_rate)):nticks_txb-int(round(tx_gap_postfix_times[i_set]*samp_rate))] = 0.805


current_settings_iq_envelope_max = np.zeros((n_sets, nticks_rxb), dtype=np.float64)
current_settings_iq_envelope_min = np.zeros((n_sets, nticks_rxb), dtype=np.float64)
current_settings_iq_envelope_avg = np.zeros((n_sets, nticks_rxb), dtype=np.float64)
current_settings_iq_envelope_square_avg = np.zeros((n_sets, nticks_rxb), dtype=np.float64)
# for i_trace in range(n_frames_per_set):
#     current_settings_iq_envelope_all[i_trace] = np.zeros((n_sets, nticks_rxb), dtype=np.float64)


# usrp.set_time_next_pps(uhd.types.TimeSpec(0))
# time.sleep(2.2)
# print("GPS Epoch time at last PPS:", usrp.get_mboard_sensor("gps_time").to_real())
# print("UHD Device time last PPS:  ", usrp.get_time_last_pps().get_real_secs())
# print("UHD Device time right now: ", usrp.get_time_now().get_real_secs())

stream_cmd.time_spec = uhd.types.TimeSpec(int(usrp.get_time_now().get_real_secs()+2.0))
rxstreamer.issue_stream_cmd(stream_cmd)

pos_mag_CSI = 0
# nsamps_left_current_frame = nticks_rxb
tick_current_frame = stream_cmd.time_spec.to_ticks(samp_rate)
pos_frame_rx = 0
pos_frame_tx = 0
nframes_received = 0
tx_in_process = False
tx_first_buf_in_a_stream = True

while True:
    while tx_in_process:
        if(pos_frame_tx + nsamps_buffer >= nticks_txb):
            tx_in_process = False
            tx_md.end_of_burst = True
        txstreamer.send(tx_buffer[0, pos_frame_tx:pos_frame_tx+nsamps_buffer], tx_md)
        tx_md.start_of_burst = False
        tx_md.has_time_spec = False
        pos_frame_tx += nsamps_buffer
        if(not tx_first_buf_in_a_stream):
           break
        tx_first_buf_in_a_stream = False
    # elif tx_triggered:
    #     tx_in_process = True
    #     pos_frame_tx = 0
    #     tx_md.start_of_burst = True
    #     tx_md.end_of_burst = False
    #     tx_md.has_time_spec = True
    #     txstreamer.send(tx_buffer[0, pos_frame_tx:pos_frame_tx+nsamps_buffer], tx_md)
    #     pos_frame_tx += nsamps_buffer
    #     if(pos_frame_tx >= nticks_txb):
    #         tx_in_process = False
    #     tx_triggered = False

    nsamps_received = rxstreamer.recv(rx_frame_buf[0, pos_frame_rx:pos_frame_rx+nsamps_buffer], rx_md)
    if rx_md.error_code != uhd.types.RXMetadataErrorCode.none:
        # print(rx_md.strerror())
        pass
    if nsamps_received:
        # print(nsamps_received)
        rx_tick_now = rx_md.time_spec.to_ticks(samp_rate)
        pos_frame_rx += nsamps_received
        # rx_frame_buf[0, (rx_tick_now-tick_current_frame):(rx_tick_now-tick_current_frame+nsamps_received)] = 
        # print(nsamps_received)
        if(pos_frame_rx > nticks_rxb):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        if(pos_frame_rx == nticks_rxb):
            # A Frame is gathered
            # Frame Processing
            # Raw IQ Forwarding
            # zmq_socket.send(rx_frame_buf[:nticks_rxb].tobytes())
            nframes_received += 1
            # # parity_tx = 1 // For debugging only
            # pos_mag_CSI = int(tick_current_frame/nticks_rxb)%len_pkt_nCSIs
            # # mag_CSIs[pos_mag_CSI] = (np.sum(np.abs(np.fft.fft(fft_window*rx_frame_buf[0, nticks_trx_gap+(1-parity_tx)*nticks_txb: -(parity_tx)*nticks_txb-nticks_trx_gap])[if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1])**2)**0.5)/(nticks_txb-(2*nticks_trx_gap))
            # # # Old Magnitude Detecting Algorithm
            # # mag_CSIs[pos_mag_CSI] = (np.sum(np.abs(np.fft.fft(rx_frame_buf[0, nticks_trx_gap+(1-parity_tx)*nticks_txb: -(parity_tx)*nticks_txb-nticks_trx_gap])[if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1])**2)**0.5)/(nticks_txb-(2*nticks_trx_gap))
            # # New Magnitude Detecting Algorithm
            # rx_frame_buf_LPF[:] = 0
            # rx_frame_buf_LPF[0, if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1] = np.fft.fft(rx_frame_buf[0, nticks_trx_gap+(1-parity_tx)*nticks_txb: -(parity_tx)*nticks_txb-nticks_trx_gap])[if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1]
            # rx_frame_buf_LPF[0, :] = np.fft.ifft(rx_frame_buf_LPF[:])
            # mag_CSIs[pos_mag_CSI] = np.mean(np.abs(rx_frame_buf_LPF))
            # if(pos_mag_CSI == len_pkt_nCSIs - 1):
            #     # A pkt is ready
            #     # udpsock.sendto(ueid.encode() + int(tick_current_frame/nticks_rxb-len_pkt_nCSIs+1).to_bytes(8, 'big', signed=False) + mag_CSIs.tobytes(), remoteaddr)
            #     udpsock.sendto(ueid.encode() + int(tick_current_frame/nticks_rxb-len_pkt_nCSIs+1).to_bytes(8, 'big', signed=False) + mag_CSIs.tobytes(), ("127.0.0.1", 1146))
            #     # udpsock.sendto("B".encode() + int(tick_current_frame/nticks_rxb-len_pkt_nCSIs+1).to_bytes(8, 'big', signed=False) + mag_CSIs.tobytes(), ("127.0.0.1", 1146))
            #     pass
            #     # print(np.mean(mag_CSIs))
            #     # zmq_socket.send(mag_CSIs.tobytes())
            # # print(pos_mag_CSI)
            
            # print(int(tick_current_frame/nticks_rxb))
            if(nframes_to_wait == 0): # Wait for the TX-RX delay
                # Scan the TX Gap configurations
                if(iframes_in_current_set == 0):
                    # Firdt sample ih this set
                    current_settings_iq_envelope_max[i_set:] = np.abs(rx_frame_buf[0, :]) # Looks like it should be [i_set, :], but coincidentally, the current version works perfectly well, so let's leave it as is.
                    current_settings_iq_envelope_min[i_set:] = np.abs(rx_frame_buf[0, :])
                    current_settings_iq_envelope_avg[i_set:] = np.abs(rx_frame_buf[0, :])
                    current_settings_iq_envelope_square_avg[i_set:] = np.square(np.abs(rx_frame_buf[0, :]))
                else:
                    current_settings_iq_envelope_max[i_set:] = np.maximum(np.abs(rx_frame_buf[0, :]), current_settings_iq_envelope_max[i_set:])
                    current_settings_iq_envelope_min[i_set:] = np.minimum(np.abs(rx_frame_buf[0, :]), current_settings_iq_envelope_min[i_set:])
                    current_settings_iq_envelope_avg[i_set:] = current_settings_iq_envelope_avg[i_set:] + np.abs(rx_frame_buf[0, :])
                    current_settings_iq_envelope_square_avg[i_set:] = current_settings_iq_envelope_square_avg[i_set:] + np.square(np.abs(rx_frame_buf[0, :]))
                
                iframes_in_current_set += 1
                if(iframes_in_current_set == n_frames_per_set):
                    # Next set
                    iframes_in_current_set = 0
                    i_set += 1
                    if(i_set == n_sets):
                        break
                        # i_set = 0
                    tx_buffer[0, :] = 0
                    tx_buffer[0, int(round(tx_gap_prefix_time*samp_rate)):nticks_txb-int(round(tx_gap_postfix_times[i_set]*samp_rate))] = 0.805
                    nframes_to_wait = nframes_to_wait_init
                    print(tx_gap_postfix_times[i_set])

                

                # # New Magnitude Detecting Algorithm
                # plt.plot(np.real(rx_frame_buf_LPF[0, :]))
                # plt.plot(np.imag(rx_frame_buf_LPF[0, :]))
                # plt.plot(np.abs(rx_frame_buf_LPF[0, :]))
                # plt.show()
                

                # exit()
            else:
                nframes_to_wait -= 1


            pos_frame_rx = 0
            tick_current_frame += nticks_rxb
            if(rx_tick_now + nsamps_received != tick_current_frame):
                # Error: rx time dismatch
                # print("Error: rx time dismatch! tick_now:", rx_tick_now, "nsamps_received: ", nsamps_received, "tick_current_frame:", tick_current_frame)
                print("E: Time dismatch")
                tick_current_frame = int((rx_tick_now+nsamps_received+nticks_rxb)/nticks_rxb)*nticks_rxb
                nsamps_to_drop = tick_current_frame - (rx_tick_now + nsamps_received)
                # print(nsamps_to_drop)
                while(nsamps_to_drop > 0):
                    nsamps_received = rxstreamer.recv(rx_frame_buf[0, 0:min(nsamps_to_drop, nsamps_buffer)], rx_md)
                    nsamps_to_drop -= nsamps_received
                # while(True):
                #     nsamps_received = rxstreamer.recv(rx_frame_buf[0, 0:nsamps_buffer], rx_md)
                #     if(rx_md.time_spec.to_ticks(samp_rate) + nsamps_received >= tick_current_frame):
                #         break
                # exit()
            
            # Tx 
            tx_md.start_of_burst = True
            tx_md.end_of_burst = False
            tx_md.has_time_spec = True
            tx_md.time_spec = uhd.types.TimeSpec.from_ticks(tick_current_frame+nticks_tx_advance, samp_rate)
            tx_in_process = True
            tx_first_buf_in_a_stream = True
            pos_frame_tx = 0
            

stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
stream_cmd.stream_now = True
rxstreamer.issue_stream_cmd(stream_cmd)

current_settings_iq_envelope_avg /= n_frames_per_set
current_settings_iq_envelope_square_avg /= n_frames_per_set

dataname = "result_TX_ro_RX_trans_X410"
np.savetxt(f"{dataname}_max.csv", current_settings_iq_envelope_max, delimiter=",")
np.savetxt(f"{dataname}_min.csv", current_settings_iq_envelope_min, delimiter=",")
np.savetxt(f"{dataname}_avg.csv", current_settings_iq_envelope_avg, delimiter=",")
np.savetxt(f"{dataname}_var.csv", current_settings_iq_envelope_square_avg - np.square(current_settings_iq_envelope_avg), delimiter=",")
# plt.plot(current_settings_iq_envelope_min[0, :])
# plt.plot(current_settings_iq_envelope_max[0, :])
# plt.plot(current_settings_iq_envelope_avg[0, :])
# plt.show()
# plt.plot(current_settings_iq_envelope_min[1, :])
# plt.plot(current_settings_iq_envelope_max[1, :])
# plt.plot(current_settings_iq_envelope_avg[1, :])
# plt.show()

current_settings_iq_envelope_var = current_settings_iq_envelope_square_avg - np.square(current_settings_iq_envelope_avg)
for i_set in range(n_sets):
    print(tx_gap_postfix_times[i_set])
    plt.plot(current_settings_iq_envelope_min[i_set, :], label='min')
    plt.plot(current_settings_iq_envelope_max[i_set, :], label='max')
    plt.plot(current_settings_iq_envelope_avg[i_set, :], label='avg')
    plt.plot(current_settings_iq_envelope_var[i_set, :], label='var')
    plt.legend()
    plt.show()

# TODO debugging only
for i_set in range(n_sets):
    print(tx_gap_postfix_times[i_set])
    plt.plot(20*np.log10(current_settings_iq_envelope_min[i_set, :]/current_settings_iq_envelope_avg[i_set, int(0.96*T_2way_measure*samp_rate)]))
    plt.plot(20*np.log10(current_settings_iq_envelope_max[i_set, :]/current_settings_iq_envelope_avg[i_set, int(0.96*T_2way_measure*samp_rate)]))
    plt.plot(20*np.log10(current_settings_iq_envelope_avg[i_set, :]/current_settings_iq_envelope_avg[i_set, int(0.96*T_2way_measure*samp_rate)]))
    plt.plot(20*np.log10(np.sqrt(current_settings_iq_envelope_var[i_set, :])/current_settings_iq_envelope_avg[i_set, :]))
    plt.show()

# TODO debugging only
for i_set in range(n_sets):
    print(tx_gap_postfix_times[i_set])
    # plt.plot(20*np.log10(current_settings_iq_envelope_min[i_set, :]/current_settings_iq_envelope_avg[i_set, 3000]))
    # plt.plot(20*np.log10(current_settings_iq_envelope_max[i_set, :]/current_settings_iq_envelope_avg[i_set, 3000]))
    # plt.plot(20*np.log10(current_settings_iq_envelope_avg[i_set, :]/current_settings_iq_envelope_avg[i_set, 3000]))
    plt.plot(20*np.log10(np.sqrt(current_settings_iq_envelope_var[i_set, :])/current_settings_iq_envelope_avg[i_set, :]))
    plt.show()