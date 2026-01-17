clear iqdata_measured
clear fft_iqdata_measured

blackman_win_100ms = blackman(4500001);
slice_length = 45000;
f_SA = 45e6;

for i_samplefile = 0:9
%     load(sprintf(iqdata_fname, i_samplefile), "Y");
%     Y = double(Y);
    raw_opts = detectImportOptions(sprintf(iqdata_fname, i_samplefile)+".txt", 'Delimiter', '\t');
    raw_opts.VariableNames = {'Key', 'Value'};
    raw_T = readtable(sprintf(iqdata_fname, i_samplefile)+".txt", raw_opts);
    raw_YScale = raw_T.Value(strcmp(raw_T.Key, 'YScale'));
    raw_fid = fopen(sprintf(iqdata_fname, i_samplefile), 'rb', 'ieee-be');
    raw_IQ = fread(raw_fid, 'int16');
    fclose(raw_fid);
    raw_I = raw_IQ(1:2:end);
    raw_Q = raw_IQ(2:2:end);
    Y = double(raw_I+1i*raw_Q)*raw_YScale;

%     Y = Y / sqrt(mean(abs(Y).^2));
    % Frequency shift compensation
    [~, pos_fft] = max(abs(fft([Y.*blackman_win_100ms; zeros(length(Y)*9, 1)])));
    
    pos_fft = pos_fft - 1;
    if(pos_fft > length(Y)*5)
        pos_fft = pos_fft - length(Y)*10;
    end
    Y = Y .* exp(-1i*2*pi*pos_fft/(length(Y)*10)*(1:length(Y)).');
    for i_slice = 1:100
        i_sample = i_samplefile*100+i_slice;
        iqdata_measured(:, i_sample) = Y((1:slice_length)+slice_length*(i_slice-1));
    %     plot(iqdata(:, i_sample));
%         fft_iqdata_measured(:, i_sample) = fft(iqdata_measured(:, i_sample));
    %     plot(10*log10(abs(fft(iqdata(:, i_sample))/max(size(iqdata(:, i_sample))))));
    end
end