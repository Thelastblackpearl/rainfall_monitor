import csv
import random
import os
import math

def create_folder(dir,folder_name: str) -> str:
    """
    Function to create a folder in a location if it does not exist
    """
    folder = dir + "/" + folder_name
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder 

def create_csv(output_dir,filename,header,data):
    """
    create a csv file using input data
    """
    path = output_dir + "/" + filename
    with open(path, mode="w", newline="") as newcsv:
        writer = csv.writer(newcsv)
        
        # Write the header
        writer.writerow(header)
        
        # Write the sorted combined data
        for row in data:
            writer.writerow(row)
            #print(f"Appended row: {row[0]}, {row[1]}")

def process_mechanical_data(input_file):
    zero_rain_rows = [] 
    non_zero_rain_rows = []
    non_zero_row_count = 0

    # Open the input file in read mode
    with open(input_file, mode="r") as infile:
        reader = csv.reader(infile)
        
        # Read the header and move to next row
        header = next(reader)
        
        # Filter rows based on rain value
        for row in reader:
            time, rain = row[0], row[1]
            
            # Check if rain value is zero or non-zero
            if float(rain) == 0:
                zero_rain_rows.append(row)
            else:
                non_zero_rain_rows.append(row)
                non_zero_row_count += 1
    
    # Calculate 10% of total non-zero rain data points
    zero_to_append_count = math.ceil(0.10 * non_zero_row_count) # round up to nearest possible integer
    print(f"Total no.of data points with non-zero rain: {non_zero_row_count}")
    print(f"Total no.of data points with zero rain: {len(zero_rain_rows)}")
    print(f"Zero rain data points to append: {zero_to_append_count}")

    # Select a random sample of zero rain data points to append
    if len(zero_rain_rows) >= zero_to_append_count:
        zero_rain_sample = random.sample(zero_rain_rows, zero_to_append_count)
    else:
        zero_rain_sample = zero_rain_rows

    # Combine zero and non-zero rows and sort them by time
    processed_data = zero_rain_sample + non_zero_rain_rows  # data structure: list of lists
    processed_data.sort(key=lambda row: row[0])  # Sort by time column (assumes time is in row[0])
    return header,processed_data
    
def main():
    # input directories
    input_mech = "/home/icfoss/hari_work/acoustic raingauge/data set/test/04-11-24/raw/davis_label.csv"
    #input_audios = "/home/icfoss/hari_work/acoustic raingauge/data set/test/04-11-24/wav"
    
    #outputs
    output_dir = "/home/icfoss/hari_work/acoustic raingauge/data set/test/04-11-24/raw" # dont use last /
    new_csv_filename = "filtered_rain.csv"

    data_dir = create_folder(output_dir,"processed data")
    audio_dir = create_folder(data_dir,"wav")
    header,data = process_mechanical_data(input_mech)
    create_csv(data_dir,new_csv_filename,header,data)
    print(f"mechanical data processing completed: output csv file contains {len(data)} data points")


if __name__ == "__main__":
    main()


# todo
# add provision to remove false mech between 5.55 am to 6.05 am
