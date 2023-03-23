import torch
import torch.nn as nn


class BiLSTM3(nn.Module):
    def __init__(self):
        super(BiLSTM3, self).__init__()
        self.lstm1 = nn.LSTM(input_size=161, hidden_size=161, num_layers=3,dropout=0.02,bidirectional=True, batch_first = True)
        self.fc = nn.Linear(161*2, 161)# fc
    def forward(self, X):
        X = torch.squeeze(X)
        pred_stft = torch.stft(X, n_fft=320,hop_length=160,win_length=320) #(Bs, F, T, 2)
        pred_stft_real, pred_stft_imag = pred_stft[:, :, :, 0], pred_stft[:, :, :, 1]
        pred_mag = torch.sqrt(pred_stft_real ** 2 + pred_stft_imag ** 2 + 1e-12)
        batch_size, m, z = pred_mag.shape # (16, 161, 103) (Bs, F, T)
        #print(out.shape)
        input = pred_mag.permute(0,2,1)#指定维度新的位置 (Bs, T, F)
        # h1 = torch.randn(3*2, batch_size, 161).to(device)  # [num_layers(=3) * num_directions(=2), batch_size, n_hidden]
        # c1 = torch.randn(3*2, batch_size, 161).to(device)

        # outputs1, (_, _) = self.lstm1(input, (h1, c1)) # (seq_length,batch_size,num_directions*hidden_size)
        outputs1, (_, _) = self.lstm1(input) # (seq_length,batch_size,num_directions*hidden_size)
        # outputs = outputs1.permute(0,2,1)   # (batch_size,seq_length,num_directions*hidden_size)
        mag=self.fc(outputs1)
        mag=mag.permute(0,2,1)
        pha = torch.atan2(pred_stft_imag, pred_stft_real)  # ([16, 161, 103])
        real = mag * torch.cos(pha)
        imag = mag * torch.sin(pha)
        model = torch.istft(torch.cat([real.unsqueeze(-1), imag.unsqueeze(-1)], dim=-1), n_fft=320, hop_length=160,
                            win_length=320)
        model = torch.unsqueeze(model,1)
        return model