clear iqdata_measured
clear fft_iqdata_measured

% blackman_win_5s = blackman(5000000);
slice_length = 100000;
% f_SA = 0.1e6;

for i_samplefile = 0:0
%     load(sprintf(iqdata_fname, i_samplefile), "Y");
%     Y = double(Y);
    [Y, f_SA] = audioread(ANdata_fname);

%     Y = Y / sqrt(mean(abs(Y).^2));
%     % Frequency shift compensation
%     [~, pos_fft] = max(abs(fft([Y.*blackman_win_5s; zeros(length(Y)*9, 1)])));
%     
%     pos_fft = pos_fft - 1;
%     if(pos_fft > length(Y)*5)
%         pos_fft = pos_fft - length(Y)*10;
%     end
%     Y = Y .* exp(-1i*2*pi*pos_fft/(length(Y)*10)*(1:length(Y)).');
    for i_slice = 1:100
        i_sample = i_samplefile*100+i_slice;
        iqdata_measured(:, i_sample) = Y((1:slice_length)+slice_length*(i_slice-1));
    %     plot(iqdata(:, i_sample));
%         fft_iqdata_measured(:, i_sample) = fft(iqdata_measured(:, i_sample));
    %     plot(10*log10(abs(fft(iqdata(:, i_sample))/max(size(iqdata(:, i_sample))))));
    end
end