import os
import pandas as pd
from tqdm import tqdm
from os import listdir
from datetime import datetime, timedelta


MECH_FILE_PATH = "/home/icfoss/hari_work/acoustic raingauge/data set/enclosure_3/24-10-24/processed/davis_label.csv"

NON_MECH_PATH = "/home/icfoss/hari_work/acoustic raingauge/data set/enclosure_3/24-10-24/processed/wav"

mech_data = pd.read_csv(MECH_FILE_PATH)
mech_data["time"] = pd.to_datetime(mech_data["time"])
wave_files = sorted(listdir(NON_MECH_PATH))


def extract_datetime_from_filename(filename):
    timestamp_str = filename.split(".")[0]
    return datetime.strptime(timestamp_str, "%Y_%m_%d_%H_%M_%S_%f")


def delete_files(filtered_wavefiles, directory):
    for wave_file in filtered_wavefiles:
        file_path = os.path.join(directory, wave_file)
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            print(f"File not found: {file_path}")


def find_files_to_delete(mech_data, wave_files):
    filtered_wavefiles = []
    checkpoint_counter = 0
    total_audios = 0
    for checkpoint in mech_data["time"]:
        checkpoint_counter = checkpoint_counter + 1
        no_of_audio_samples = 0
        for wave_file in wave_files:
            file_datetime = extract_datetime_from_filename(wave_file)
            if checkpoint - timedelta(minutes=3) <= file_datetime <= checkpoint:
                filtered_wavefiles.append(wave_file)
                no_of_audio_samples = no_of_audio_samples + 1
        total_audios = total_audios + no_of_audio_samples
        print(f"checkpoint {checkpoint_counter} :",checkpoint," & ","no. of audio samples in the checkpoint:",no_of_audio_samples) 
    print("total audio samples collected:",total_audios)           
    print("no. of audio samples need to be deleted:",len(list(set(wave_files) - set(filtered_wavefiles))))
    return list(set(wave_files) - set(filtered_wavefiles))


delete_files(find_files_to_delete(mech_data, wave_files), NON_MECH_PATH)
print("deleted unwanted audio files")

# add provision to know total number of audio samples in each checkpoint
# find checkpoints with 0 audio samples
# add provision to know total number of audio samples in each checkpoint
# find checkpoints with 0 audio samples