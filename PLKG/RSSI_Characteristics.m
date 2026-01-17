%% Load raw RSSI data
% CSIdata_fname = "../TDD_Channel_Measuring/data/2170MHz_902_3mdist_N210_5ksps_202601_f32.wav";
% [raw_rssi, fs_rssi] = audioread(CSIdata_fname);
% raw_rssi = raw_rssi(5e6-1e5:5.5e6+1e5, :); % Walking

CSIdata_fname = "../TDD_Channel_Measuring/data/2170MHz_902_4mdist_N210_5ksps_202601_f32.wav";
[raw_rssi, fs_rssi] = audioread(CSIdata_fname);
raw_rssi = raw_rssi(0.5e6-1e5:1e6+1e5, :); % Sitting

% CSIdata_fname = "../TDD_Channel_Measuring/data/2170MHz_905_dynamic_3mdist_N210_5ksps_202601_f32.wav";
% [raw_rssi, fs_rssi] = audioread(CSIdata_fname);
% raw_rssi = raw_rssi(1e6-1e5:1.5e6+1e5, :); % Dynamic

%% PLKG
L = 1;
k = 2;
key_generation;

%% RSSI Distributions
fig4_obj = figure(1);
fig4_obj.Position(3:4) = [600, 250];
ax1 = subplot(1,2,1);
ax2 = subplot(1,2,2);

observed_samples = rssi_in_a_box(:, 1);

axes(ax1)
plot((0:size(observed_samples, 1)-1)/fs_rssi, observed_samples)
ylim([-box_size*0.75, box_size*0.75])
grid on;

min_value = min(observed_samples);
max_value = max(observed_samples);
var_value = var(observed_samples);
hist_nbins = 50;
hist_nsamples = numel(observed_samples);
hist_binsize = (max_value-min_value)/hist_nbins;
hist_edges = (0:hist_nbins)*hist_binsize+min_value;
axes(ax2)
histogram(observed_samples, hist_edges)
xlim([-box_size*0.75, box_size*0.75])
xticks([])
view(90, -90)

ax1.Position = [0.11,0.18,0.68,0.81];
ax1.FontName = "Times New Roman";
ax1.FontSize = 12;
ax2.Position = [0.8,0.18,0.18,0.81];
ax2.FontName = "Times New Roman";

ax2.FontSize = 12;
axes(ax1)
xlabel("$$t (s)$$", 'Interpreter', 'Latex');
ylabel("$$\tilde{S}_u$$", 'Interpreter', 'Latex')
% xticks(0:200:800);
% xticks = num2str(ax1.get('xTick')','%d');
% xticks((size(xticks, 1)), :) = ' ';
% ax1.set('xTickLabel',xticks);
%% Autocorrelations
fig2_obj = figure(2);
fig2_obj.Position(3:4) = [600, 250];
plot((-size(rssi_in_a_box, 1):size(rssi_in_a_box, 1)-2)/fs_rssi, xcorr(rssi_in_a_box(:, 1), 'normalized'));
hold on;
plot((-size(rssi_HP, 1):size(rssi_HP, 1)-2)/fs_rssi, xcorr(rssi_HP(:, 1), 'normalized'));
xlim([-1,1])
xlabel("Time difference ($$s$$)", 'Interpreter', 'Latex')
ylabel("Normalized autocorrelations")
box on;
grid on;
ax1 = gca;
ax1.Position = [0.09,0.18,0.9,0.79];
ax1.FontName = "Times New Roman";
ax1.FontSize = 12;
legend(["$$\tilde{S}_u$$", "$$S''_u$$"], 'Interpreter', 'Latex')