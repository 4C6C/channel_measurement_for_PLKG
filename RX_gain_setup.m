% TX PostGap Set: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

figure_handle = figure(1);
figure_handle.Position(3:4) = [600, 400];

f_s = [12.5e6, 12.5e6, 6.25e6];
devnames = ["N210", "N310", "X410"];
nticks_to_show = 0.02*f_s;
colors = [[1,0,0];[0,0.5,0];[0,0,1];[0.3,0.2,0];[0,0,0]];
for i_trace = 1:3
    temp20250721min = csvread("result_RX_gain_setup_"+devnames(i_trace)+"_min.csv");
    temp20250721max = csvread("result_RX_gain_setup_"+devnames(i_trace)+"_max.csv");
    temp20250721avg = csvread("result_RX_gain_setup_"+devnames(i_trace)+"_avg.csv");
    xtick_ms = (0:size(temp20250721avg(1:nticks_to_show(i_trace)), 1)-1)/f_s(i_trace)*1e3;
    mkr_idx = 1:ceil(size(temp20250721avg(1:nticks_to_show(i_trace)), 1)/20):size(temp20250721avg(1:nticks_to_show(i_trace)), 1);
    reference_ticks = [round(0.02*f_s(i_trace)): round(0.03*f_s(i_trace))];
    hold on
%     plot(xtick_us, 20*log10(temp20250721min(i_set, :)) - mean(20*log10(temp20250721avg(i_set, (150*f_s/1e6):(180*f_s/1e6)))))
%     plot(xtick_us, 20*log10(temp20250721max(i_set, :)) - mean(20*log10(temp20250721avg(i_set, (150*f_s/1e6):(180*f_s/1e6)))))
%     plot(xtick_us, 20*log10(temp20250721avg(i_set, :)) - mean(20*log10(temp20250721avg(i_set, (150*f_s/1e6):(180*f_s/1e6)))), "Color", colors(i_trace, :))
%     plot(xtick_ms, 20*log10(temp20250721max(1:nticks_to_show(i_trace))/mean(temp20250721avg(reference_ticks))), "Marker", "s", "Color", colors(i_trace, :), "MarkerIndices", mkr_idx)
%     plot(xtick_ms, 20*log10(temp20250721min(1:nticks_to_show(i_trace))/mean(temp20250721avg(reference_ticks))), "Marker", "+", "Color", colors(i_trace, :), "MarkerIndices", mkr_idx)
    plot(xtick_ms, 20*log10(temp20250721avg(1:nticks_to_show(i_trace))/mean(temp20250721avg(reference_ticks))), "Color", colors(i_trace, :), "MarkerIndices", mkr_idx)
end
legend_handle = legend(devnames, "Interpreter", "Latex");
xlabel("Time after RX gain setting ($$\mathrm{ms}$$)", "Interpreter", "Latex")
ylabel("aAveraged mplitude deviation in $$\mathrm{dB}$$", "Interpreter", "Latex")
ax = gca;
ax.Position = [0.09,0.115,0.89,0.86];
ylim([-32 18]);
grid on;
box on;
ax.FontName = "Times New Roman";
ax.FontSize = 12;
legend_handle.FontName = "Times New Roman";
legend_handle.FontSize = 12;
