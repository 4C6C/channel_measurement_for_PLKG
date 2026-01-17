%% Acquire Measured IQ data
% ANdata_fnames = ["AN_data\\X410_RX_amplitude.wav", "AN_data\\N310_RX_amplitude.wav", "AN_data\\N210_RX_amplitude.wav"];
ANdata_fnames = ["AN_data\\N210_RX_amplitude_atten36dB_TXG31dB_RXG20dB.wav", "AN_data\\N210_RX_amplitude_atten36dB_TXG31dB_RXG18dB.wav", "AN_data\\N210_RX_amplitude_atten36dB_TXG29dB_RXG20dB.wav", "AN_data\\N210_RX_amplitude_atten38dB_TXG31dB_RXG20dB.wav", "AN_data\\N310_RX_amplitude.wav", "AN_data\\X410_RX_amplitude.wav"];
% colors = ["b", "r", "g", "c", "k", "r"];
for i_data = 1:size(ANdata_fnames,2)
    ANdata_fname = ANdata_fnames(i_data);
    AN_data_slicing;
    %% Magnitude Noise - PSDf

    fft_window = blackman(slice_length);
    % % fft_window = ones(slice_length, 1);
    amp_correction_factor = length(fft_window)/sum(fft_window);


    freq_resolution_Hz = f_SA / slice_length;
    mean_psd_iqdata = (mean(abs(fft(iqdata_measured.*fft_window*amp_correction_factor, [], 1)).^2, 2))/size(iqdata_measured, 1)^2;
    mean_psd_abs_iqdata = (mean(abs(fft(abs(iqdata_measured).*fft_window*amp_correction_factor, [], 1)).^2, 2))/size(iqdata_measured, 1)^2;
    mean_psd_iqdata_ssb = (mean_psd_iqdata + mean_psd_iqdata([1, end:-1:2]))/2;
    mean_psd_abs_iqdata_ssb = (mean_psd_abs_iqdata + mean_psd_abs_iqdata([1, end:-1:2]))/2;

    % mean_psd_iqdata = (mean(abs(fft((iqdata_measured*0+0.2).*blackman_win*amp_correction_factor, [], 1)).^2, 2));
    % mean_psd_abs_iqdata = (mean(abs(fft(abs((iqdata_measured*0+0.2)).*blackman_win*amp_correction_factor, [], 1)).^2, 2));

    freq_tick_psd = (0:slice_length-1)*freq_resolution_Hz;
    digifreq_span = (2:floor(slice_length/2));

    figure(1)
    % semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_iqdata(digifreq_span)/mean_psd_iqdata(1)/freq_resolution_Hz)); % dBc/Hz
    semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_iqdata_ssb(digifreq_span)/(mean(mean(abs(iqdata_measured)))^2)/freq_resolution_Hz)); % dBc/Hz
    hold on
    % f1p2 = semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_abs_iqdata_ssb(digifreq_span)/freq_resolution_Hz), "r"); % dBV/Hz

    % f1p4 = yline(10*log10(mean(mean(abs(iqdata_measured)))^2), "--");

end
%% Figure Layout
fig1_obj = figure(1);
ylim([-160, -60])
xlim([10^1, 10*10^3])
fig1_obj.Position(3:4) = [600, 400];

xlabel("$$f(\mathrm{Hz})$$", 'Interpreter', 'Latex');
ylabel("$$\mathrm{PSD} \; (\mathrm{dBc/Hz})$$", 'Interpreter', 'Latex');
% legend_handle = legend([f1p1], ["$$r_{L}(t)$$"], 'Interpreter', 'Latex');
legend_handle = legend(["N210, TX gain = 31dB, RX gain = 20dB, atten = 36dB", ...
                        "N210, TX gain = 31dB, RX gain = 18dB, atten = 36dB", ...
                        "N210, TX gain = 29dB, RX gain = 20dB, atten = 36dB", ...
                        "N210, TX gain = 31dB, RX gain = 20dB, atten = 38dB", ...
                        "N310, atten = 36dB", ...
                        "X410, atten = 36dB"]);
ax = gca;
grid on;
ax.Position = [0.11,0.12,0.85,0.85];
ax.FontName = "Times New Roman";
ax.FontSize = 12;
legend_handle.FontName = "Times New Roman";
legend_handle.FontSize = 12;

% 
% y_phase = angle(Y)
% y_phase = angle(Y);
% plot(10*log10(abs(fft(y_phase))))
% plot(y_phase
% plot(y_phase)
% y_phase_delta = diff(y_phase)
% y_phase_delta = diff(y_phase);
% plot(y_phase_delta)
% y_phase_delta2 = mod(y_phase_delta, 2*pi)
% y_phase_delta2 = mod(y_phase_delta, 2*pi);
% plot(y_phase_delta2)
% plot(y_phase_delta+pi)
% y_phase_delta2 = mod(y_phase_delta+pi, 2*pi);
% plot(y_phase_delta2)
% plot(y_phase_delta2-pi)
% y_phase_delta2 = mod(y_phase_delta+pi, 2*pi)-pi;
% plot(y_phase_delta2)
% y_phase_delta3 = cumsum(y_phase(1), y_phase_delta2);
% y_phase_delta3 = cumsum([y_phase(1), y_phase_delta2]);
% y_phase_delta3 = cumsum([y_phase(1), y_phase_delta2.']);
% plot(y_phase)
% hold on
% plot(y_phase_delta3)
% plot(10*log10(abs(fft(y_phase_delta3))))
% 0:4
% xlabel([0:4500000]/4500000*45e6)
% plot(10*log10(abs(fft(y_phase_delta3))))
% [0:4500000]/4500000*45e6;
% plot([0:4500000]/4500000*45e6, 10*log10(abs(fft(y_phase_delta3))))
% plot(y_phase_delta3)
% y_phase_delta3 = cumsum([y_phase(1), y_phase_delta2.' - mean(y_phase_delta2]));
% y_phase_delta4 = cumsum([y_phase(1), y_phase_delta2.' - mean(y_phase_delta2)]);
% plot(y_phase_delta4)
% plot(10*log10(abs(fft(y_phase_delta4))))
% hold on
% plot(10*log10(abs(fft(Y))))
% histogram(y_phase_delta4)
% plot(y_phase_delta4
% plot(y_phase_delta4)
% plot(10*log10(abs(fft(Y))))
% plot(y_phase_delta3)
% plot(y_phase_delta2)
% histogram(y_phase_delta2)
% aaa = y_phase_delta2 / sqrt(mean(y_phase_delta2.^2))
% aaa = y_phase_delta2 / sqrt(mean(y_phase_delta2.^2));
% histogram(aaa)
% bbb = norm()