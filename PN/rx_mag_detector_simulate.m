s_slices_per_store = 100;
rx_len_sec = 1e-3;
rx_len_nsamps = round(rx_len_sec*f_SA);
rng(1919810);
slice_length = 45000;

W_ps = [5e3, 10e3, 25e3, 100e3, 500e3, 1e6];
for W_p = W_ps
    W_p_SSB = W_p/2;
    n_lpf = 5/(W_p/f_SA);
    lpf_iq = fir1(n_lpf, W_p_SSB/f_SA*2, hamming(n_lpf+1)).';
    n_store = 1;
    % dBm_to_dBV = -13.01;
    dBm_to_dBV = -10.00; % 1V in SA = 10dBm (I path or Q path only)
    for i_store = 1:n_store
        % AWGN
    %     P_AWGN_dBc = -60;
        N0_dBm_per_Hz = -174 + 10-10000; % Do not add AWGN here
        P_Carrier_dBm = -6;
        iqdata_simulated_awgn = sqrt(10^(0.1*(P_Carrier_dBm+dBm_to_dBV)))*iqdata_simulated(:, i_store) + sqrt((10^(0.1*(N0_dBm_per_Hz+dBm_to_dBV)))*f_SA)*sqrt(1/2)*(wgn(size(iqdata_simulated, 1), 1, 1, 1)+1i*wgn(size(iqdata_simulated, 1), 1, 1, 1));

        % LPF
        iqdata_simulated_awgn_lpf = conv(iqdata_simulated_awgn, lpf_iq, 'valid');
    %     iqdata_simulated_awgn_lpf = iqdata_simulated_awgn;

        fprintf("slice %d\n", i_store)
        % slicing & PSD
        for i_slice = 1:100
            i_sample = (i_store-1)*100+i_slice;
            iqdata_simulated_awgn_lpf_sliced(:, i_sample) = iqdata_simulated_awgn_lpf((1:slice_length)+slice_length*(i_slice-1));
        %     plot(iqdata(:, i_sample));
    %         fft_iqdata_measured(:, i_sample) = fft(iqdata_measured(:, i_sample));
        %     plot(10*log10(abs(fft(iqdata(:, i_sample))/max(size(iqdata(:, i_sample))))));
        end
    end
    %% Magnitude Noise - PSD

    % fft_window = blackman(slice_length);
    fft_window = ones(slice_length, 1);
    amp_correction_factor = length(fft_window)/sum(fft_window);


    freq_resolution_Hz = f_SA / slice_length;
    mean_psd_iqdata = (mean(abs(fft(iqdata_simulated_awgn_lpf_sliced.*fft_window*amp_correction_factor, [], 1)).^2, 2))/size(iqdata_simulated_awgn_lpf_sliced, 1)^2;
    mean_psd_abs_iqdata = (mean(abs(fft(abs(iqdata_simulated_awgn_lpf_sliced).*fft_window*amp_correction_factor, [], 1)).^2, 2))/size(iqdata_simulated_awgn_lpf_sliced, 1)^2;
    mean_psd_iqdata_ssb = (mean_psd_iqdata + mean_psd_iqdata([1, end:-1:2]))/2;
    mean_psd_abs_iqdata_ssb = (mean_psd_abs_iqdata + mean_psd_abs_iqdata([1, end:-1:2]))/2;

    % mean_psd_iqdata = (mean(abs(fft((iqdata_measured*0+0.2).*blackman_win*amp_correction_factor, [], 1)).^2, 2));
    % mean_psd_abs_iqdata = (mean(abs(fft(abs((iqdata_measured*0+0.2)).*blackman_win*amp_correction_factor, [], 1)).^2, 2));

    freq_tick_psd = (0:slice_length-1)*freq_resolution_Hz;
    digifreq_span = (2:floor(slice_length/2));

    figure(1)
    % semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_iqdata(digifreq_span)/mean_psd_iqdata(1)/freq_resolution_Hz)); % dBc/Hz
    f1p1 = semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_iqdata_ssb(digifreq_span)/freq_resolution_Hz)-dBm_to_dBV-P_Carrier_dBm, "b"); % dBm/Hz
    hold on
    f1p2 = semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_abs_iqdata_ssb(digifreq_span)/freq_resolution_Hz)-dBm_to_dBV-P_Carrier_dBm, "r"); % dBm/Hz
end

grid on
fig1_obj = figure(1);
ylim([-180, -70])
xlim([10^3, 20*10^6])
fig1_obj.Position(3:4) = [600, 400];

xlabel("Baseband frequency offset$$(\mathrm{Hz})$$");
ylabel("$$\mathrm{PSD} (\mathrm{dBc/Hz})$$");
legend_handle = legend([f1p1, f1p2], ["$$y_{l}[n]$$", "$$|y_{l}[n]|$$"]);
ax = gca;
grid on;
ax.Position = [0.11,0.12,0.85,0.85];
ax.FontName = "Times New Roman";
ax.FontSize = 12;
legend_handle.FontName = "Times New Roman";
legend_handle.FontSize = 12;



% n_lpf = 10000;
% lpf_iq = fir1(n_lpf, 0.0001);
% % plot(real(lpf_iq));
% % hold on 
% % plot(imag(lpf_iq));
% % iqdata_simulated_awgn_lpf = filtfilt(lpf_iq, iqdata_simulated_awgn);
% % iqdata_simulated_awgn_lpf = conv(lpf_iq.', iqdata_simulated_awgn);
% % iqdata_simulated_awgn_lpf = iqdata_simulated_awgn;
% 
% mag_results = zeros(1, N_of_runs);
% for i_runs = 1:N_of_runs
%     iqdata_simulated_awgn_lpf = conv(lpf_iq.', iqdata_simulated_awgn((i_runs-1)*rx_len_nsamps+1:i_runs*rx_len_nsamps));
%     y_rxb = iqdata_simulated_awgn_lpf;
% %     y_rxb = iqdata_simulated_awgn_lpf((i_runs-1)*rx_len_nsamps+1:i_runs*rx_len_nsamps);
%     mag_results(i_runs) = mean(abs(y_rxb(n_lpf:rx_len_nsamps)));
% end

% Fs = 45e6;      % sample rate
% R = 5;          % decimator factor
% D = 1;          % differential delay
% N = 3;          % number of stage
% Fp = 4e3;      % pass band
% Fstp = 5e3;   % stop band
% Ap = 0.1;       % attenuation in pass band
% Astp = 60;      % attenuation in stop band
% CICDecim = dsp.CICDecimator(R, D, N);
% CICCompDecim = dsp.CICCompensationDecimator(CICDecim, ...
%  'DecimationFactor',2,'PassbandFrequency',Fp, ...
%  'StopbandFrequency',Fstp,'SampleRate',Fs/R);
