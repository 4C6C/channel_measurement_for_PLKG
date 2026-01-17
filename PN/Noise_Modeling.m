%% Acquire Measured IQ data
iqdata_fname = "SA_IQ_data\\N210_iq_45Msps_25MHzIF_PNO_BC_%04d.bin";
iqdata_measured_slicing;

%% Magnitude Noise - PSD

% fft_window = blackman(slice_length);
fft_window = ones(slice_length, 1);
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
f1p1 = semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_iqdata_ssb(digifreq_span)/freq_resolution_Hz), "b"); % dBV/Hz
hold on
f1p2 = semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_abs_iqdata_ssb(digifreq_span)/freq_resolution_Hz), "r"); % dBV/Hz

%% Magnitude Noise - PDF
fig2_obj = figure(2);
fig2_obj.Position(3:4) = [600, 400];
ax1 = subplot(1,2,1);
ax2 = subplot(1,2,2);

i_observe = 1;
observed_samples = reshape(iqdata_measured(:, ((i_observe-1)*100+1):(i_observe*100)), [], 1);
min_mag = min(abs(observed_samples));
max_mag = max(abs(observed_samples));
mean_mag = mean(abs(observed_samples));
var_mag = var(abs(observed_samples));
hist_nbins = 100;
hist_nsamples = numel(observed_samples);
hist_binsize = (max_mag-min_mag)/hist_nbins;
hist_edges = (0:hist_nbins)*hist_binsize+min_mag;

axes(ax1)
plot(abs(observed_samples(1:1000)))
ylim([min_mag-sqrt(var_mag), max_mag+sqrt(var_mag)])
grid on;

axes(ax2)
histogram(abs(observed_samples), hist_edges)
% Nornal Distribution
pdf_nd = @(x) 1/sqrt(2.*pi.*var_mag).*exp(-(x-mean_mag).^2/(2.*var_mag));
hold on;
plot(hist_edges, pdf_nd(hist_edges)*hist_binsize*hist_nsamples, 'LineWidth', 1);
xlim([min_mag-sqrt(var_mag), max_mag+sqrt(var_mag)])
view(90, -90)

ax1.Position = [0.135,0.12,0.65,0.85];
ax1.FontName = "Times New Roman";
ax1.FontSize = 12;
ax2.Position = [0.8,0.12,0.18,0.85];
ax2.FontName = "Times New Roman";
ax2.FontSize = 12;
axes(ax1)
xlabel("n");
ylabel("$$|r[n]|$$ (Volts)", 'Interpreter', 'Latex')
xticks(0:200:800);
% xticks = num2str(ax1.get('xTick')','%d');
% xticks((size(xticks, 1)), :) = ' ';
% ax1.set('xTickLabel',xticks);


axes(ax2)
ylabel("N of Samples")
xticks([])
yticks([0 100000])
yticks_text = num2str(ax2.get('yTick')','%d');
yticks_text(2:(size(yticks_text, 1)-1), :) = ' ';
ax2.set('yTickLabel',yticks_text);

%% Phase Extraction
% for i_slice = 1:1
clear phase_deltas;
clear phase_accumulated;
for i_slice = 1:size(iqdata_measured, 2)
    phase_iqdata = angle(iqdata_measured(:, i_slice));
    phase_delta = diff(phase_iqdata);
    phase_delta = mod(phase_delta+pi, 2*pi)-pi;
    phase_deltas(:, i_slice) = [phase_delta; 0];
    phase_accumulated(:, i_slice) = cumsum([phase_iqdata(1), phase_delta.']).';
end
% mean_psd_phase_delta = (mean(abs(fft(phase_deltas.*fft_window*amp_correction_factor, [], 1)).^2, 2))/size(iqdata_measured, 1)^2;
mean_psd_phase_accumulated = (mean(abs(fft(phase_accumulated.*fft_window*amp_correction_factor, [], 1)).^2, 2))/size(iqdata_measured, 1)^2;
% mean_psd_phase_delta_ssb = (mean_psd_phase_delta + mean_psd_phase_delta([1, end:-1:2]))/2;
mean_psd_phase_accumulated_ssb = (mean_psd_phase_accumulated + mean_psd_phase_accumulated([1, end:-1:2]))/2;

figure(1)
% semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_phase_delta_ssb(digifreq_span)/freq_resolution_Hz)); % dBrad/Hz
f1p3 = semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_phase_accumulated_ssb(digifreq_span)*mean(mean(abs(iqdata_measured)))^2/freq_resolution_Hz), 'Color', [0 0.5 0]); % dBV/Hz
f1p4 = yline(10*log10(mean(mean(abs(iqdata_measured)))^2), "--");

fig3_obj = figure(3);
fig3_obj.Position(3:4) = [600, 400];
semilogx((1:size(iqdata_measured, 1))/f_SA, angle(iqdata_measured(:, 1)/iqdata_measured(1, 1)))
hold on
for i_slice = 2:10
    semilogx((1:size(iqdata_measured, 1))/f_SA, angle(iqdata_measured(:, i_slice)/iqdata_measured(1, i_slice)))
end
xlim([1/f_SA, 0.001])
xlabel("t (s)");
ylabel("$$\angle (r_{L}(t)) - \angle (r_{L}(0)) (\mathrm{rad})$$", 'Interpreter', 'Latex');
ax = gca;
grid on;
ax.Position = [0.11,0.12,0.85,0.85];
ax.FontName = "Times New Roman";
ax.FontSize = 12;

%% PSD of PN
% mean_psd_Ar_phase_accumulated_corrected = mean_psd_phase_accumulated_ssb*mean(mean(abs(iqdata_measured)))^2 - mean_psd_abs_iqdata_ssb;
% mean_psd_Ar_phase_accumulated_corrected = max(eps, mean_psd_phase_accumulated_ssb*mean(mean(abs(iqdata_measured)))^2 - mean_psd_abs_iqdata_ssb);
% mean_psd_Ar_phase_accumulated_corrected(1) = max(eps, mean_psd_Ar_phase_accumulated_corrected(1) - (mean(mean(abs(iqdata_measured)))^2));
digi_freq_range_AWGN = round((4e6-100e3)/freq_resolution_Hz):round((4e6+100e3)/freq_resolution_Hz);
mean_psd_n_r_n_ssb = mean(mean_psd_abs_iqdata_ssb(digi_freq_range_AWGN));
mean_psd_Ar_phase_accumulated_corrected = max(eps, mean_psd_phase_accumulated_ssb*mean(mean(abs(iqdata_measured)))^2 - mean_psd_n_r_n_ssb);
mean_psd_phase_corrected = mean_psd_Ar_phase_accumulated_corrected / (mean(mean(abs(iqdata_measured)))^2);
figure(1)
f1p5 = semilogx(freq_tick_psd(digifreq_span), 10*log10(mean_psd_Ar_phase_accumulated_corrected(digifreq_span)/freq_resolution_Hz), 'Color', [0.8 0 0.8]); % dBV/Hz
f1p6 = yline(10*log10(mean_psd_n_r_n_ssb/freq_resolution_Hz), "-", 'Color', [0.5 0.4 0.2]); % dBV/Hz

%% phi[n+1]-phi[n] - PDF
fig4_obj = figure(4);
fig4_obj.Position(3:4) = [600, 400];
ax1 = subplot(1,2,1);
ax2 = subplot(1,2,2);

i_observe = 1;
observed_samples = reshape(iqdata_measured(:, ((i_observe-1)*100+1):(i_observe*100)), [], 1);
observed_values = angle(observed_samples(2:end)./observed_samples(1:end-1));
min_value = min(observed_values);
max_value = max(observed_values);
mean_value = mean(observed_values);
var_value = var(observed_values);
hist_nbins = 100;
hist_nsamples = numel(observed_values);
hist_binsize = (max_value-min_value)/hist_nbins;
hist_edges = (0:hist_nbins)*hist_binsize+min_value;

axes(ax1)
plot(observed_values(1:1000))
ylim([min_value-sqrt(var_value), max_value+sqrt(var_value)])
grid on;

axes(ax2)
histogram(observed_values, hist_edges)
% Nornal Distribution
pdf_nd = @(x) 1/sqrt(2.*pi.*var_value).*exp(-(x-mean_value).^2/(2.*var_value));
hold on;
plot(hist_edges, pdf_nd(hist_edges)*hist_binsize*hist_nsamples, 'LineWidth', 1);
xlim([min_value-sqrt(var_value), max_value+sqrt(var_value)])
view(90, -90)

ax1.Position = [0.085,0.12,0.7,0.83];
ax1.FontName = "Times New Roman";
ax1.FontSize = 12;
ax2.Position = [0.8,0.12,0.18,0.83];
ax2.FontName = "Times New Roman";
ax2.FontSize = 12;
axes(ax1)
xlabel("n");
ylabel("$$\phi_{TX}[n+1]-\phi_{TX}[n]$$ (rad)", 'Interpreter', 'Latex')
xticks(0:200:800);
% xticks = num2str(ax1.get('xTick')','%d');
% xticks((size(xticks, 1)), :) = ' ';
% ax1.set('xTickLabel',xticks);


axes(ax2)
ylabel("N of Samples")
xticks([])
yticks([0 100000])
yticks_text = num2str(ax2.get('yTick')','%d');
yticks_text(2:(size(yticks_text, 1)-1), :) = ' ';
ax2.set('yTickLabel',yticks_text);

%% Figure Layout
fig1_obj = figure(1);
ylim([-160, 0])
xlim([10^3, 20*10^6])
fig1_obj.Position(3:4) = [480, 400];

obj_xlabel = xlabel("$$f - f_c (\mathrm{Hz})$$", 'Interpreter', 'Latex');
obj_ylabel = ylabel("$$\mathrm{PSD} (\mathrm{dBV/Hz})$$", 'Interpreter', 'Latex');
obj_ylabel.Position(1) = 435;
legend_handle = legend([f1p1, f1p2, f1p3, f1p5, f1p6], ["$$r_{L}(t)$$", "$$|r_{L}(t)|$$", "$$A_r\angle (r_{L}(t))$$", "$$A_r\tilde{\phi}_{TX}(t)$$", "$$\hat{n}_{rn}(t)$$"], 'Interpreter', 'Latex');
ax = gca;
grid on;
ax.Position = [0.125,0.125,0.86,0.85];
ax.FontName = "Times New Roman";
ax.FontSize = 12;
legend_handle.FontName = "Times New Roman";
legend_handle.FontSize = 12;
set(legend_handle, 'Position',[0.16 0.622902306149415 0.25 0.22030995534718]);

% textbox
annotation(fig1_obj,'textbox',...
    [0.16 0.844118653798336 0.326759599985908 0.073960267280585],...
    'String',{sprintf('$$A_r^2=%.2f\\mathrm{dBv}$$', 10*log10(mean(mean(abs(iqdata_measured)))^2))},...
    'LineStyle','none',...
    'Interpreter','latex',...
    'FontSize',12,...
    'FontName','Times New Roman');

% arrow
annotation(fig1_obj,'arrow',[0.153333333333333 0.183333333333333],...
    [0.943055944055944 0.904095904095904]);

% arrow
annotation(fig1_obj,'arrow',[0.851666666666667 0.79],[0.239 0.526]);

ax_zoomin = copyobj(ax, fig1_obj);
set(ax_zoomin,'FontName','Times New Roman','FontSize',12,'Position',[0.541666666666667 0.538 0.433333333333334 0.374],'XMinorTick','on');
xlabel(ax_zoomin, []); ylabel(ax_zoomin, []);
xlim(ax_zoomin,[807261.730806994 22499000]);
ylim(ax_zoomin,[-153.816237238697 -127.894992707827]);
xticks(ax_zoomin, [1e6,1e7]);

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