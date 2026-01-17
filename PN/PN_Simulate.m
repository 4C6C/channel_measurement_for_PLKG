P_TRx = 2*mean_psd_phase_corrected;
len_P = length(P_TRx);
P_TRx_diff = P_TRx.*abs((1-exp(-1i*2*pi*(0:len_P-1)/len_P)).').^2;
rng(114514);

f_s = 45e6;
n_samples = f_s * 0.101;
n_slices = 10;
for i_slice = 1:n_slices
    % Generation of phi_diff
    phi_diff = conv(randn(n_samples+1*len_P, 1)*sqrt(len_P), real(ifft(sqrt(abs(P_TRx_diff)).*exp(-1i*pi*((0:len_P-1)).'))));
    phi_diff = phi_diff(len_P:end-len_P);

    % Generation of phi
    phi_simulated(:, i_slice) = cumsum(phi_diff);

    % Generation of iqdata
    iqdata_simulated(:, i_slice) = exp(1i*phi_simulated(:, i_slice));
end

clear iqdata_measured
clear fft_iqdata_measured

blackman_win_100ms = blackman(4500000*1.01);
slice_length = 45000;
f_SA = 45e6;

% for i_samplefile = 0:9
% %     Y = iqdata_simulated(i_samplefile*4500000+1:((i_samplefile+1)*4500000));
%     Y = iqdata_simulated(:, i_samplefile+1);
% %     Y = Y / sqrt(mean(abs(Y).^2));
%     % Frequency shift compensation
%     [~, pos_fft] = max(abs(fft([Y.*blackman_win_100ms; zeros(length(Y)*9, 1)])));
%     pos_fft = pos_fft - 1;
%     if(pos_fft > length(Y)*5)
%         pos_fft = pos_fft - length(Y)*10;
%     end
%     Y = Y .* exp(-1i*2*pi*pos_fft/(length(Y)*10)*(1:length(Y)).');
%     for i_slice = 1:100
%         i_sample = i_samplefile*100+i_slice;
%         iqdata_measured(:, i_sample) = Y((1:slice_length)+slice_length*(i_slice-1));
%     %     plot(iqdata(:, i_sample));
% %         fft_iqdata_measured(:, i_sample) = fft(iqdata_measured(:, i_sample));
%     %     plot(10*log10(abs(fft(iqdata(:, i_sample))/max(size(iqdata(:, i_sample))))));
%     end
% end

% semilogx(freq_tick_psd(digifreq_span), 10*log10(P_TRx(digifreq_span)/freq_resolution_Hz));






% 
% 
% figure(1)
% f1p5 = semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_Ar_phase_accumulated_corrected(digifreq_span)/freq_resolution_Hz), 'Color', [0.8 0 0.8]); % dBV/Hz
