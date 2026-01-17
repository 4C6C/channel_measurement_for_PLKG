%% Load raw RSSI data
CSIdata_fname = "../TDD_Channel_Measuring/data/2170MHz_902_1mdist_N210_5ksps_202601_f32.wav";
[raw_rssi_walking_1m, fs_rssi] = audioread(CSIdata_fname);
raw_rssi_walking_1m = raw_rssi_walking_1m(1e6-1e5:1.5e6+1e5, :); % Walking

CSIdata_fname = "../TDD_Channel_Measuring/data/2170MHz_902_3mdist_N210_5ksps_202601_f32.wav";
[raw_rssi_walking_3m, fs_rssi] = audioread(CSIdata_fname);
raw_rssi_walking_3m = raw_rssi_walking_3m(5e6-1e5:5.5e6+1e5, :); % Walking

CSIdata_fname = "../TDD_Channel_Measuring/data/2170MHz_902_2mdist_N210_5ksps_202601_f32.wav";
[raw_rssi_sitting_2m, fs_rssi] = audioread(CSIdata_fname);
raw_rssi_sitting_2m = raw_rssi_sitting_2m(0.5e6-1e5:1e6+1e5, :); % Sitting

CSIdata_fname = "../TDD_Channel_Measuring/data/2170MHz_902_4mdist_N210_5ksps_202601_f32.wav";
[raw_rssi_sitting_4m, fs_rssi] = audioread(CSIdata_fname);
raw_rssi_sitting_4m = raw_rssi_sitting_4m(0.5e6-1e5:1e6+1e5, :); % Sitting

CSIdata_fname = "../TDD_Channel_Measuring/data/2170MHz_905_dynamic_3mdist_N210_5ksps_202601_f32.wav";
[raw_rssi_dynamic_3m, fs_rssi] = audioread(CSIdata_fname);
raw_rssi_dynamic_3m = raw_rssi_dynamic_3m(1e6-1e5:1.5e6+1e5, :); % Dynamic

raw_rssis = cell(4, 1);
raw_rssis{1} = raw_rssi_walking_1m; raw_rssis{2} = raw_rssi_walking_3m; raw_rssis{3} = raw_rssi_sitting_2m; raw_rssis{4} = raw_rssi_sitting_4m; raw_rssis{5} = raw_rssi_dynamic_3m;
Ls = [0.05, 0.05, 0.01, 0.01, 1];
mkrs = ['+', 's', 'o', '*', 'v'];
drop_fading = [false, false, false, false, true];


%% PLKG
fig1_obj = figure(1);
fig1_obj.Position(3:4) = [600, 400];
fig2_obj = figure(2);
fig2_obj.Position(3:4) = [600, 400];
for i_scenario = 1:5
    raw_rssi = raw_rssis{i_scenario};
    L = Ls(i_scenario);
    ks = 1:8;
    KDRs = [];
    for k = ks
        key_generation;
        KDRs = [KDRs, KDR];
    end
    figure(1)
    hold on
    plot(ks, KDRs, 'Marker', mkrs(i_scenario));
    figure(2)
    hold on
    plot((-size(rssi_in_a_box_sampled, 1)+1:size(rssi_in_a_box_sampled, 1)-1), xcorr(rssi_in_a_box_sampled(:, 1), 'normalized'))
end

%% Figure layout
figure(1)
box on
grid on
legend(["Walking, $$d_{\mathrm{AB}}=1\mathrm{m}$$", "Walking, $$d_{\mathrm{AB}}=3\mathrm{m}$$", "Sitting, $$d_{\mathrm{AB}}=2\mathrm{m}$$", "Sitting, $$d_{\mathrm{AB}}=4\mathrm{m}$$", "Dynamic, $$d_{\mathrm{AB}}=3\mathrm{m}$$"], 'Interpreter', 'latex')
xlabel("$$k$$", 'Interpreter', 'latex')
ylabel("KDR")
ax = gca;
grid on;
box on;
ax.Position = [0.095,0.11,0.89,0.87];
ax.FontName = "Times New Roman";
ax.FontSize = 12;

figure(2)
plot((-size(rssi_in_a_box_sampled, 1)+1:size(rssi_in_a_box_sampled, 1)-1), xcorr(rand(size(rssi_in_a_box_sampled, 1), 1)-0.5, 'normalized'))
box on
grid on
legend(["Walking, $$d_{\mathrm{AB}}=1\mathrm{m}$$", "Walking, $$d_{\mathrm{AB}}=3\mathrm{m}$$", "Sitting, $$d_{\mathrm{AB}}=2\mathrm{m}$$", "Sitting, $$d_{\mathrm{AB}}=4\mathrm{m}$$", "Dynamic, $$d_{\mathrm{AB}}=3\mathrm{m}$$", "MATLAB-generated random sequence"], 'Interpreter', 'latex')
xlabel("$$\Delta n$$", 'Interpreter', 'latex')
ylabel("Normalized autocorrelations")
xlim([-1000 1000])
ax = gca;
grid on;
box on;
ax.Position = [0.095,0.11,0.89,0.87];
ax.FontName = "Times New Roman";
ax.FontSize = 12;