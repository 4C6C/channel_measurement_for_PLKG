import zmq
import socket
import numpy as np
import time
import uhd
import matplotlib.pyplot as plt
import sys
from scipy import signal
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
samp_rate = 12.5e6
tx_lo_freq = 2170e6
# rx_lo_freq = tx_lo_freq
rx_lo_offset = -10e6
# tx_lo_offset = -50e6
tx_lo_offset = 0e6
rxgain = 0
# rxgain = 27
agc_enabled = True
# txgain = 25.5
txgain = 31
# ueid = "A"
csi_host_addr = ("127.0.0.1", 1146)
if(len(sys.argv) < 2):
    print("Invalid parameter! ")
    exit()
ueid = sys.argv[1]
timing_correction_for_uA = 0
T_2way_measure = 200e-6 
T_TX_Postfix_gap = 20e-6
T_TX_Advance = 24e-6
T_Rx_Postfix_gap = 4e-6
nticks_tx_postfix_gap = int(T_TX_Postfix_gap*samp_rate)
T_txb = (T_2way_measure/2)+T_TX_Advance
nticks_valid_rxdata = int(((T_2way_measure/2)-T_TX_Advance-T_Rx_Postfix_gap)*samp_rate)
if(ueid == "A"):
    # parity_tx = 0
    usrp_addr = "192.168.10.2"
    port_udpsock = 19198
    timing_correction = timing_correction_for_uA
elif(ueid == "B"):
    # parity_tx = 1
    usrp_addr = "192.168.10.3"
    port_udpsock = 19199
    timing_correction = -T_2way_measure/2
else:
    print("Invalid UEID!")
    exit()
tx_timing_calibration_nsample = -43
# t_tx_delay = 50e-3 + (T_2way_measure/2) - T_TX_Advance # TX slot control and compensate for the streaming delay
t_tx_delay = round(50e-3/T_2way_measure)*T_2way_measure + (T_2way_measure/2) - T_TX_Advance # TX slot control and compensate for the streaming delay
nticks_rxb = int(T_2way_measure*samp_rate)
nticks_txb = int(T_txb*samp_rate)
# nticks_trx_gap = int(T_trx_gap*samp_rate)
nticks_tx_delay = int(t_tx_delay*samp_rate)+tx_timing_calibration_nsample
# digi_if_freq = (1/nticks_valid_rxdata)*int(T_2way_measure*1.25e6)
digi_if_freq = 0.25
print("digi_freq:", digi_if_freq * samp_rate)
rx_lo_freq = tx_lo_freq
# freq_tolerance = 12.5e3
freq_tolerance = 2500e3 # For new magnitude detection algorithm
nfft = nticks_valid_rxdata
nfft_tolerance = int(round(freq_tolerance/(samp_rate/nfft)))
if_fftpos = int(digi_if_freq*nfft)
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

# usrp = uhd.usrp.MultiUSRP("addr="+usrp_addr+", clock_source=gpsdo,time_source=gpsdo, master_clock_rate=125e6")
usrp = uhd.usrp.MultiUSRP("addr="+usrp_addr)
usrp.set_rx_freq(uhd.types.TuneRequest(rx_lo_freq, rx_lo_offset), 0)
usrp.set_rx_rate(samp_rate, 0)
usrp.set_rx_gain(rxgain, 0)
usrp.set_rx_antenna("TX/RX", 0)
usrp.set_tx_freq(uhd.types.TuneRequest(tx_lo_freq, tx_lo_offset), 0)
usrp.set_tx_rate(samp_rate, 0)
usrp.set_tx_gain(txgain, 0)

# # Timing source: GPSDO
# usrp.set_clock_source("gpsdo")
# usrp.set_time_source("gpsdo")
# Timing source: External
usrp.set_clock_source("external")
usrp.set_time_source("external")

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

# Time sync (External PPS, PC Time)
while(not usrp.get_mboard_sensor("ref_locked", 0).to_bool()):
    time.sleep(0.5)
print("Reference locked.")

pc_time = int(time.time())
while (pc_time == int(time.time())):
    time.sleep(0.01)
pc_time = int(time.time())
usrp.set_time_next_pps(uhd.types.TimeSpec(pc_time + 1.0 + timing_correction))
# usrp.set_time_next_pps(uhd.types.TimeSpec(0))
time.sleep(2.2)
print("UHD Device time last PPS:  ", usrp.get_time_last_pps().get_real_secs())
print("UHD Device time right now: ", usrp.get_time_now().get_real_secs())


class AGC_Controller:
    def __init__(self, tgt_BB_power_dBc=-15, pwr_tolerance_dB=6,  overload_BB_pwr_dBc=-2, initial_gain_dB=0.0, max_gain_dB = 31.5, min_gain_dB = 0):
        self.tgt_BB_power_dBc = tgt_BB_power_dBc
        self.pwr_tolerance_dB = pwr_tolerance_dB
        self.overload_BB_pwr_dBc = overload_BB_pwr_dBc
        self.gain_dB = initial_gain_dB
        self.max_gain_dB = max_gain_dB
        self.min_gain_dB = min_gain_dB
        self.gain_dB_last = 0

        self.current_period = None
        self.BB_power_dBc_sum = 0
        self.power_count = 0

        self.overload_this_sec = False

    def update(self, power_dBc, t):
        i_period = int(t*4)
        if power_dBc > self.overload_BB_pwr_dBc:
            self.gain_dB = 0
            self.overload_this_sec = True
            self.gain_dB_last = 0
            return self.gain_dB
        if self.current_period is None:
            self.start_new_period(i_period)
            self.gain_dB_last = self.gain_dB
            return self.gain_dB
        elif i_period != self.current_period:
            gain_adjustment = self.process_last_period()
            self.start_new_period(i_period)
            return gain_adjustment

        
        self.BB_power_dBc_sum += power_dBc
        self.power_count += 1
        return None

    def start_new_period(self, i_period):
        self.current_period = i_period
        self.BB_power_dBc_sum = 0
        self.power_count = 0
        self.overload_this_sec = False

    def process_last_period(self):
        if self.overload_this_sec:
            return None
        if self.power_count == 0:
            return None
        BB_power_dBc_avg = self.BB_power_dBc_sum / self.power_count
        error_dB =  BB_power_dBc_avg - self.tgt_BB_power_dBc

        if abs(error_dB) > self.pwr_tolerance_dB:
            new_gain = np.clip(self.gain_dB -error_dB, self.min_gain_dB, self.max_gain_dB)
            gain_changed = (new_gain != self.gain_dB)
            self.gain_dB = new_gain
            return (self.gain_dB if gain_changed else None)
agc_controller = AGC_Controller(tgt_BB_power_dBc=-10)
tgt_size_buffer_nsamps = 2500 # 1250/5
st_args = uhd.usrp.StreamArgs("fc32", "sc16")
st_args.channels = [0]
rx_md = uhd.types.RXMetadata()
rxstreamer = usrp.get_rx_stream(st_args)
nsamps_buffer = min(rxstreamer.get_max_num_samps(), tgt_size_buffer_nsamps)
rx_buffer = np.zeros((1, nsamps_buffer), dtype=np.complex64)
rx_frame_buf = np.zeros((1, nticks_rxb), dtype=np.complex64)
tx_buffer = np.zeros((1, nticks_txb), dtype=np.complex64)
txstreamer = usrp.get_tx_stream(st_args)
tx_md = uhd.types.TXMetadata()
bpf_fir_025fs = np.complex64([0.000351365255466787, 0.00253972884267899, 0.00873090040342958, 0.0185627386677737, 0.0249359943205045, 0.0156864014954709, -0.0143211820165310, -0.0483750911476621, -0.0487927460690288, 0.0166902763512510, 0.139958205754721, 0.263644834255122, 0.315759661450750, 0.263644834255122, 0.139958205754721, 0.0166902763512510, -0.0487927460690288, -0.0483750911476621, -0.0143211820165310, 0.0156864014954709, 0.0249359943205045, 0.0185627386677737, 0.00873090040342958, 0.00253972884267899, 0.000351365255466787])
bpf_fir_025fs = bpf_fir_025fs * np.exp(2j*np.pi*digi_if_freq*np.arange(np.size(bpf_fir_025fs)))
halflen_firbpf = int(np.floor((np.size(bpf_fir_025fs)-1)/2))
rx_frame_buf_LPF = np.zeros((1, nfft-np.size(bpf_fir_025fs)+1), dtype=np.complex64)
# tx_md.start_of_burst = True
# tx_md.end_of_burst = True
# tx_md.has_time_spec = True
# tx_buffer[0, :] = 0.9*np.exp(2j*np.pi*digi_if_freq*np.arange(np.size(tx_buffer)))
tx_buffer[0, :] = 0.9*np.exp(2j*np.pi*digi_if_freq*np.arange(np.size(tx_buffer)))
# tx_buffer[0, :] = 0.9
tx_buffer[0, nticks_txb-nticks_tx_postfix_gap:] = 0
# tx_buffer[0, 100:] = 0 // For timing debugging only
mag_CSIs = np.zeros(len_pkt_nCSIs, dtype=np.float32)
print("RX buffer size:", nsamps_buffer)
stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
stream_cmd.stream_now = False
print("Waiting for CSI Collecter...")
# while(True):
#     (msg, remoteaddr) = udpsock.recvfrom(1500)
#     if(msg == b"Start!"):
#         break
print("CSI Collecter is online.")

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
            # parity_tx = 1 // For debugging only
            pos_mag_CSI = int(tick_current_frame/nticks_rxb)%len_pkt_nCSIs
            # mag_CSIs[pos_mag_CSI] = (np.sum(np.abs(np.fft.fft(fft_window*rx_frame_buf[0, nticks_trx_gap+(1-parity_tx)*nticks_txb: -(parity_tx)*nticks_txb-nticks_trx_gap])[if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1])**2)**0.5)/(nticks_txb-(2*nticks_trx_gap))
            # # Old Magnitude Detecting Algorithm
            # mag_CSIs[pos_mag_CSI] = (np.sum(np.abs(np.fft.fft(rx_frame_buf[0, nticks_trx_gap+(1-parity_tx)*nticks_txb: -(parity_tx)*nticks_txb-nticks_trx_gap])[if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1])**2)**0.5)/(nticks_txb-(2*nticks_trx_gap))
            # New Magnitude Detecting Algorithm
            # rx_frame_buf_LPF[:] = 0
            # rx_frame_buf_LPF[0, if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1] = np.fft.fft(rx_frame_buf[0, 0: nticks_valid_rxdata])[if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1]
            # rx_frame_buf_LPF[0, :] = np.fft.ifft(rx_frame_buf_LPF[:])
            # rx_frame_buf_LPF[:] = 
            rx_frame_buf_LPF[0, :] = signal.fftconvolve(rx_frame_buf[0, 0: nticks_valid_rxdata], bpf_fir_025fs, mode="valid")
            mag_CSIs[pos_mag_CSI] = np.mean(np.abs(rx_frame_buf_LPF))
            if(agc_enabled):
                gain_adjustment = agc_controller.update(20*np.log10(mag_CSIs[pos_mag_CSI]), rx_md.time_spec.get_real_secs())
                if(not gain_adjustment is None):
                    rxgain = gain_adjustment
                    usrp.set_rx_gain(rxgain, 0)
                    print("Gain:", gain_adjustment)
            if(pos_mag_CSI == len_pkt_nCSIs - 1):
                # A pkt is ready
                # udpsock.sendto(ueid.encode() + int(tick_current_frame/nticks_rxb-len_pkt_nCSIs+1).to_bytes(8, 'big', signed=False) + mag_CSIs.tobytes(), remoteaddr)
                udpsock.sendto(ueid.encode() + int(tick_current_frame/nticks_rxb-len_pkt_nCSIs+1).to_bytes(8, 'big', signed=False) + mag_CSIs.tobytes(), csi_host_addr)
                # udpsock.sendto("A".encode() + int(tick_current_frame/nticks_rxb-len_pkt_nCSIs+1).to_bytes(8, 'big', signed=False) + mag_CSIs.tobytes(), ("127.0.0.1", 1146))
                pass
                # print(np.mean(mag_CSIs))
                # zmq_socket.send(mag_CSIs.tobytes())
            # print(pos_mag_CSI)
            
            # print(int(tick_current_frame/nticks_rxb))
            if(nframes_received == 1000):
                plt.plot(np.real(rx_frame_buf[0, :]))
                plt.plot(np.imag(rx_frame_buf[0, :]))
                plt.plot(np.abs(rx_frame_buf[0, :]))
                rx_frame_valid = np.zeros(np.size(rx_frame_buf), dtype=np.complex64)
                rx_frame_valid[0: nticks_valid_rxdata] = rx_frame_buf[0, 0: nticks_valid_rxdata]
                plt.plot(np.real(rx_frame_valid[:]))
                plt.show()
                a = np.abs(np.fft.fft(rx_frame_valid[halflen_firbpf: nticks_valid_rxdata-halflen_firbpf]))
                plt.plot(a)
                # b = np.zeros(np.size(a), dtype=np.float32)
                # b[if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1] = a[if_fftpos-nfft_tolerance:if_fftpos+nfft_tolerance+1]
                b = np.abs(np.fft.fft(rx_frame_buf_LPF[0, :]))
                plt.plot(b)
                plt.show()

                # New Magnitude Detecting Algorithm
                plt.plot(np.real(rx_frame_buf_LPF[0, :]))
                plt.plot(np.imag(rx_frame_buf_LPF[0, :]))
                plt.plot(np.abs(rx_frame_buf_LPF[0, :]))
                plt.show()
                

            #     # exit()



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
            tx_md.time_spec = uhd.types.TimeSpec.from_ticks(tick_current_frame+nticks_tx_delay, samp_rate)
            tx_in_process = True
            tx_first_buf_in_a_stream = True
            pos_frame_tx = 0
            
