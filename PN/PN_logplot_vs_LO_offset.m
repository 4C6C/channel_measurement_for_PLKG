PN_logplot_data_LO_offset_0MHz = csvread("SA_logplot_with_TX_LO_offset\PN_logplot_LO_Offset_0MHz_N310.csv");
PN_logplot_data_LO_offset_50MHz = csvread("SA_logplot_with_TX_LO_offset\PN_logplot_LO_Offset_50MHz_N310.csv");

fig5_obj = figure(5);
f1p1 = semilogx(PN_logplot_data_LO_offset_0MHz(:, 1), PN_logplot_data_LO_offset_0MHz(:, 2), "b"); % dBc/Hz
hold on
f1p2 = semilogx(PN_logplot_data_LO_offset_50MHz(:, 1), PN_logplot_data_LO_offset_50MHz(:, 2), "r"); % dBc/Hz






fig5_obj.Position(3:4) = [600, 400];

obj_xlabel = xlabel("$$f - f_c (\mathrm{Hz})$$", 'Interpreter', 'Latex');
obj_ylabel = ylabel("$$\mathrm{PSD} (\mathrm{dBc/Hz})$$", 'Interpreter', 'Latex');
% obj_ylabel.Position(1) = 435;
legend_handle = legend([f1p1, f1p2], ["$$f_s \omega_x = 0 \mathrm{Hz}$$", "$$f_s \omega_x = 50 \mathrm{MHz}$$"], 'Interpreter', 'Latex');

grid on; box on;

ax = gca;
ax.Position = [0.105,0.125,0.87,0.85];
ax.FontName = "Times New Roman";
ax.FontSize = 12;
legend_handle.FontName = "Times New Roman";
legend_handle.FontSize = 12;