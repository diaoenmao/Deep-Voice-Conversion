import numpy as np
import torch
from torch.utils.data import Dataset
import json
import random
from pathlib import Path
import os
from hydra import utils
import pandas as pd
import chardet


class CPCDataset_sameSeq(Dataset):
    def __init__(self, root, n_sample_frames, mode):
        self.root = Path(root)
        self.n_sample_frames = n_sample_frames

        self.speakers = sorted(os.listdir(root/f'{mode}/mels'))
        
        with open(self.root / f"{mode}.json") as file:
            metadata = json.load(file)
        self.metadata = []
        for mel_len, mel_out_path, lf0_out_path in metadata:
            # if mel_len > n_sample_frames: # only select wavs having frames>=140
            mel_out_path = Path(mel_out_path)
            lf0_out_path = Path(lf0_out_path)
            speaker = mel_out_path.parent.stem
            self.metadata.append([speaker, mel_out_path, lf0_out_path])
        print('n_sample_frames:', n_sample_frames, 'metadata:', len(self.metadata))
        random.shuffle(self.metadata)

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, index):
        dataset_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(dataset_dir, 'Dataset/PromptTTS/Real_training.csv')
        with open(csv_file_path, 'rb') as df:
            result = chardet.detect(df.read())
# Read the file using the detected encoding
        df = pd.read_csv('/Users/chaelin/Deep-Voice-Conversion/Dataset/PromptTTS/Real_training.csv', encoding=result['encoding'].lower())

        # csv_file_path = ".../Dataset/PromptTTS/Real_training.csv"
        # df = pd.read_csv(csv_file_path)
        
        speaker, mel_path, lf0_path = self.metadata[index]

        mel_path = self.root.parent / mel_path
    
        # Get the Caption through csv
        item_name = str(mel_path).split('.')[0].split('\\')[-1]
        
        # Find the row in dataframe where "item_name" matches the value
        matched_row = df[df['item_name'] == item_name]

        if len(matched_row) > 0:
            # If we found a match, return the "style_prompt" value of the matched row
            caption = matched_row['style_prompt'].values[0]
        else:
            caption = ''
        
        # lf0_path = self.root.parent / lf0_path
        mel = np.load(mel_path).T
        # lf0 = np.load(lf0_path)
        melt = mel
        # lf0t = lf0
        while mel.shape[-1] < self.n_sample_frames:
            mel = np.concatenate([mel, melt], -1)
        #     lf0 = np.concatenate([lf0, lf0t], 0)
        # zero_idxs = np.where(lf0 == 0.0)[0]
        # nonzero_idxs = np.where(lf0 != 0.0)[0]
        # if len(nonzero_idxs) > 0 :
        #     mean = np.mean(lf0[nonzero_idxs])
        #     std = np.std(lf0[nonzero_idxs])
        #     if std == 0:
        #         lf0 -= mean
        #         lf0[zero_idxs] = 0.0
        #     else:
        #         lf0 = (lf0 - mean) / (std + 1e-8)
        #         lf0[zero_idxs] = 0.0

        pos = random.randint(0, mel.shape[-1] - self.n_sample_frames)
        mel = mel[:, pos:pos + self.n_sample_frames]
        # lf0 = lf0[pos:pos + self.n_sample_frames]
        return torch.from_numpy(mel), caption, index

# root_path = Path(utils.to_absolute_path("data"))
# dataloader = CPCDataset_sameSeq(
#     root=root_path,
#     n_sample_frames=128, # 128
#     mode='train')
# # for i, (mels, mels_ids) in enumerate(dataloader, 1):
# #     # lf0 = lf0.to(device)
# #     if i == 2:
# #         break
# #     print(mels.shape)
# #     print(mels)
# #     print(mels_ids)
# print(dataloader.__getitem__(0))
current_path = os.getcwd()
print("Current path:", current_path)

dataset_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(dataset_dir, 'Dataset/PromptTTS/Real_training.csv')
with open(csv_file_path, 'rb') as df:
    result = chardet.detect(df.read())
# Read the file using the detected encoding
df = pd.read_csv('Deep-Voice-Conversion/Dataset/PromptTTS/Real_training.csv', encoding=result['encoding'].lower())
  
# csv_file_path = 'Dataset/PromptTTS/Real_training.csv'
# df = pd.read_csv(csv_file_path)

