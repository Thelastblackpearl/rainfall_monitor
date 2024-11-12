import csv
import random
import os
import math
from datetime import datetime, timedelta
from os import listdir
import shutil
from typing import List


def extract_timestamp_from_filename(filename: str) -> datetime:
    """
    extract time stamp from audio file name  
    """
    timestamp_str = filename.split(".")[0]
    return datetime.strptime(timestamp_str, "%Y_%m_%d_%H_%M_%S_%f")

def create_folder(dir: str, folder_name: str) -> str:
    """
    Function to create a folder in a location if it does not exist
    """
    folder = os.path.join(dir, folder_name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder 

def clean_directory(dir: str) -> None:
    """
    Delete all audio files to avoid issues from random sampling of zero data points, 
    as running the code multiple times on same data set and directory may leave unnecessary files.
    """
    count = 0
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        os.remove(file_path)
        count += 1
    print(f"Deleted audio files from previous session: {count}")

def generate_csv(output_dir: str, filename: str, header: list[str], data: list[list[str]]) -> None:
    """
    create a csv file using input data
    """
    path = os.path.join(output_dir,filename)
    with open(path, mode="w", newline="") as newcsv:
        writer = csv.writer(newcsv)
        
        # Write the header
        writer.writerow(header)
        
        # Write data
        for row in data:
            writer.writerow(row)
            #print(f"Appended row: {row[0]}, {row[1]}")

def check_sample_numbers(wav_files: list[str], row: list[str]) -> bool:
    """
    check no.of samples in a specific time frame
    """
    audios = [] # temporary list for storing wavs of each time data
    time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f") # convert timestamp date type (str to datetime.datetime)
    for wav_file in wav_files:
        file_datetime = extract_timestamp_from_filename(wav_file)
        if time - timedelta(minutes=3) <= file_datetime <= time:
            audios.append(wav_file) #append wav file to temp list
    if len(audios) >= 17:
        # print(f"{row} sufficient data points = {len(audios)}")
        return True
    else:
        print(f"{row} insufficient no.of audio samples,{len(audios)} only: discarding data point")
        return False
    
def collect_audio_samples(wav_files: list[str], csv_data: list[list[str]]) -> list[str]:
    """
    create a list of audio samples corresponding to the time check points in input data 
    """
    audios = []
    for row in csv_data:
        time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f") # convert timestamp date type (str to datetime.datetime)
        for wav in wav_files:
            file_datetime = extract_timestamp_from_filename(wav)
            if time - timedelta(minutes=3) <= file_datetime <= time:
                audios.append(wav) #append wav file to temp list
    return audios

def copy_audios(audios : list[str], source_dir: str, destination_dir: str) -> None: # add doc string
    """
    copy audio files to a specific directory
    """
    # create wav folder with in destination dir for audio
    destination_dir = create_folder(destination_dir,"wav")

    clean_directory(destination_dir) # clean wav directory before copying
    
    for audio in audios:
        source_path = os.path.join(source_dir, audio)

        # Copy the file to the destination
        try:
            shutil.copy2(source_path, destination_dir) # preserve metadata of file
            # print(f"Copied '{audio}' to {destination_dir}")
        except FileNotFoundError:
            print(f"File '{audio}' not found in source directory.")
        except Exception as e:
            print(f"Error copying '{audio}': {e}")
    print("copying completed")        

def false_data_filter(data: list[list[str]]) -> list[list[str]]:
    """
    remove false data from mech.raingauge between 5.55 am to 6.05 am
    """
    process_data = []
    for inner_list in data:
        for item in inner_list:
            time, rain = item[0], item[1]
            # Convert timestamp string to datetime object
            time_dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
            print(time_dt)
            min_time = datetime.strptime("05:55:00.000000", "%H:%M:%S.%f")
            max_time = datetime.strptime("06:05:00.000000", "%H:%M:%S.%f")
            if rain == 0.2 and min_time <= time_dt <= max_time:  
                print (f"{item} found false value and discarding it")
            else:
                data.append(item)
    return process_data
  
def process_data(input_file: str, wav_files: list[str]) -> tuple[list[str],list[list[str]]]:
    zero_rain_rows = [] 
    non_zero_rain_rows = []
    non_zero_row_count = 0
    zero_row_count = 0
    
    # Open the input file in read mode
    with open(input_file, mode="r") as infile:
        reader = csv.reader(infile)
        
        # Read the header and move to next row
        header = next(reader)
        
        # Filter rows based on rain value
        for row in reader:
            if check_sample_numbers(wav_files,row):
                rain = row[1] # assume rain data is in coloumn two

                # Check if rain value is zero or non-zero
                if float(rain) == 0:
                    zero_row_count += 1
                    zero_rain_rows.append(row)
                    # wav_main.append(wav_temp)
                else:
                    non_zero_row_count += 1
                    non_zero_rain_rows.append(row) # append csv to list for new csv 
                    #audio_main.append(audio_temp)  # appending wave to main list
                                               
    
    # Calculate 10% of total non-zero rain data points
    zero_to_append_count = math.ceil(0.10 * non_zero_row_count) # round up to nearest possible integer

    # Select a random sample of zero rain data points to append
    if len(zero_rain_rows) >= zero_to_append_count:
        zero_rain_sample = random.sample(zero_rain_rows, zero_to_append_count)
    else:
        zero_rain_sample = zero_rain_rows

    # Combine zero and non-zero rows and sort them by time
    processed_data = zero_rain_sample + non_zero_rain_rows  # data structure: list of lists
    processed_data.sort(key=lambda row: row[0])  # Sort by time column (assumes time is in row[0])
    #processed_data = false_data_filter(processed_data) # delete false interrupt data 

    print("input details")
    print(f"input csv contain {zero_row_count + non_zero_row_count} data points: zero data points = {zero_row_count} & non-zero data points = {non_zero_row_count}")
    print(f"Total no.of input wav files: {len(wav_files)}")
    print(f"Zero rain data points to append: {zero_to_append_count}")

    return header, processed_data
    
def main():
    # input directories
    input_mech = "/home/icfoss/hari_work/acoustic raingauge/data set/test/04-11-24/raw/davis_label.csv"
    input_audios = "/home/icfoss/hari_work/acoustic raingauge/data set/test/04-11-24/raw/wav"
    
    #outputs
    output_dir = "/home/icfoss/hari_work/acoustic raingauge/data set/test/04-11-24" # dont use last /
    new_csv_filename = "filtered_rain.csv"
    
    data_dir = create_folder(output_dir,"processed data")
    wav_files = sorted(listdir(input_audios)) # wav_files datatype list[str]
    csv_header, csv_data = process_data(input_mech,wav_files)
    generate_csv(data_dir,new_csv_filename,csv_header,csv_data)
    audios = collect_audio_samples(wav_files,csv_data) # audios datatype list[str]
    copy_audios(audios,input_audios, data_dir)
    print("output")
    print(f"total mech data ponits: {len(csv_data)} & total audio files: {len(audios)}")




if __name__ == "__main__":
    main()


# todo
# add provision to remove false mech between 5.55 am to 6.05 am (false value filtering)
    #   error false value filtering 
    #   error in timestamp format 
# use standard name for variables,type hinting,documentation
# it is found that there is change in no.of audio files copying to new location
    # this might be happening because, we are selecting random zero datapoint samples
    # since no.of samples in each point can be 17 or 18 

# Potential issue: 
# random zero sampling could cause errors in audio file copying.
    # Running the code multiple times on the same inputs may leave behind unnecessary audio files from previous execution.