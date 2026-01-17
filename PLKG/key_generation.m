%% Drop data with deep fading or dynamic environment
if(drop_fading)
    meanpwr = mean(abs(raw_rssi).^2);
    i_drop = (raw_rssi(:, 1)<sqrt(meanpwr(1)*10^(-1.5))) | (raw_rssi(:, 2)<sqrt(meanpwr(2)*10^(-1.5)));
    raw_rssi = raw_rssi(~i_drop, :);
end

%% mag -> dBFs
rssi_dBFs = 20*log10(raw_rssi);

%% LPF
rssi_LP = filter(flter_test2, rssi_dBFs);

%% Sample time alignment (prediction-based)
aa = interp(rssi_LP(:, 1), 2);
aa = aa((1:size(rssi_LP, 1))*2);
rssi_LP(:, 1) = aa;

%% HPF
rssi_HP = filter(flter_test1, rssi_LP);
rssi_HP = rssi_HP(1e5:end-1e5, :);

%% Compression
% box_size = 0.01;
box_size = L;
rssi_HP = log(1+abs(rssi_HP)/box_size/2)*box_size*2.*sign(rssi_HP);

%% level segmentation
rssi_in_a_box = mod(rssi_HP + (box_size/2), box_size)-(box_size/2);

%% sampling
sampling_interval_nsamples = 125;
rssi_in_a_box_sampled = downsample(rssi_in_a_box, sampling_interval_nsamples);

%% Quantization, Gray Mapping, and calculate KDR
M = 2^k;
rssi_quantized = min(floor((rssi_in_a_box_sampled+(box_size/2))/box_size*M),M-1);
if(k == 1)
    gray_base = uint64([0;1]);
elseif(k == 2)
    gray_base = uint64([0;1;3;2]);
else
    gray_k = gen_gray_code(k);
    gray_base = uint64(sum(2.^((k-1):-1:0).*gray_k, 2));
end

bits_generated = size(rssi_quantized, 1)*k;
key_A = gray_base(rssi_quantized(:, 1)+1);
key_B = gray_base(rssi_quantized(:, 2)+1);
bits_error = biterr(key_A, key_B);
KDR = bits_error / bits_generated;

%% Functions
function gray_code=gen_gray_code(N)
    sub_gray=[0;1];
    for n=2:N
        if N==2
            gray_code=sub_gray;
        elseif N>2
            top_gray=[zeros(1,2^(n-1))' sub_gray];
            bottom_gray=[ones(1,2^(n-1))' sub_gray];
            bottom_gray=bottom_gray(end:-1:1,:);
            sub_gray=[top_gray;bottom_gray];
        end
    gray_code=sub_gray;
    end
end