import logging
import subprocess
import pandas as pd
from os import path, listdir
import RPi.GPIO as GPIO
from datetime import datetime, timedelta
from utils.estimate import estimate_rainfall, load_estimate_model
from utils.connectivity import send_data_via_internet, send_data_via_lorawan
from plugins.battery_monitor import setup_serial_connection, preprocess_dataframe
from plugins.moisture_sensor import read_moisture_sensor
from utils.helper import (
    time_stamp_fnamer,
    load_config,
    create_folder,
    delete_files
)


def record_audio(file_path, duration, file_format, resolution, sampling_rate):
    subprocess.call(
        [
            "arecord",
            "-q",
            "--duration=" + str(duration),
            "-t",
            str(file_format),
            "-f",
            str(resolution),
            "-r",
            sampling_rate,
            file_path,
        ]
    )


def initialize_logging(log_dir, audio_log_filename, start_time, total_samples):
    create_folder(log_dir)
    logging.basicConfig(
        filename=path.join(log_dir, audio_log_filename),
        filemode="a+",
        format="%(message)s",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("*******************************************************")
    logger.info(f"Started data logging at {start_time}\n")
    logger.info(f"Total number of samples to be recorded: {total_samples}\n")
    return logger


def log_time_remaining(logger, end_time):
    time_left = end_time - datetime.now()
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    log_message = f"Time left: {days} days {hours} hours {minutes} minutes and {seconds} seconds\n"
    logger.info(log_message)


def write_rain_data_to_csv(result_data, log_dir, rain_log_filename):
    result_df = pd.DataFrame(result_data)
    result_df.to_csv(path.join(log_dir, rain_log_filename), index=False)


def send_data(config, mm_hat, solar_V, battery_V, solar_I, battery_I):
    if config["communication"] == "LORAWAN":
        send_data_via_lorawan(mm_hat, solar_V, battery_V, solar_I, battery_I)
    else:
        send_data_via_internet(mm_hat, solar_V, battery_V, solar_I, battery_I)


def main():
    config = load_config("config.yaml")
    db_counter, rain = 0, 0
    DB_write_interval = config["DB_writing_interval_min"]
    result_data = []
    num_subsamples = config["infer_inetrval_sec"] // config["sample_duration_sec"]
    record_hours = config["record_hours"]
    field_deployed = config["field_deployed"]
    end_time = datetime.now() + timedelta(hours=record_hours)
    min_threshold = config["min_threshold"]
    moisture_threshold = config["moisture_threshold"]
    infer_model_path = path.join(config["infer_model_dir"],config["infer_model_name"])
    infer_model = load_estimate_model(infer_model_path)
    locations = []
    # serial commuication setup for battery monitoring
    ser = setup_serial_connection(config["uart_port"], config["baudrate"])

    try:
        if field_deployed:
            i = 1 # audio sample number
            while True:
                dt_now = datetime.now()
                print(f"Recording sample number {i} on {dt_now}")
                audio_fname = time_stamp_fnamer(dt_now) + ".wav"
                location = path.join(config["data_dir"], audio_fname)
                record_audio(
                    location,
                    config["sample_duration_sec"],
                    config["file_format"],
                    config["resolution"],
                    config["sampling_rate"],
                )
                locations.append(location)

                if i % num_subsamples == 0: # if (infer_inetrval // wav_duration) no of audio subsamples are collected
                    mm_hat = estimate_rainfall(infer_model, locations) # estimating rainfall
                    print("Estimated rainfall: ", mm_hat)

                    files_and_directories = listdir(config["data_dir"])
                    files_to_delete = [
                        path.join(config["data_dir"], f)
                        for f in files_and_directories
                        if path.isfile(path.join(config["data_dir"], f))
                    ]

                    delete_files(files_to_delete)
                    locations.clear()

                    rain += mm_hat
                    db_counter += 1

                    # reading moisture sensor
                    moisture = read_moisture_sensor(channel=0, gain=1)

                    # reading battery parameters
                    # solar_V, battery_V, solar_I, battery_I = 17.2, 15.2, 1.5, 2.2
                    solar_V, battery_V, solar_I, battery_I = (preprocess_dataframe(ser))

                    # sending data to DB
                    if db_counter == DB_write_interval:
                        if moisture and moisture < moisture_threshold and rain >= min_threshold:
                            send_data(config, mm_hat, solar_V, battery_V, solar_I, battery_I)
                        else:
                            send_data(config, 0.0, solar_V, battery_V, solar_I, battery_I)
                        rain, db_counter = 0, 0
                i += 1

        else:
            logger = initialize_logging(
                config["log_dir"],
                config["audio_log_filename"],
                datetime.now(),
                int(record_hours * (3600 / config["sample_duration_sec"])),
            )
            for i in range(1, int(record_hours * (3600 / config["sample_duration_sec"])) + 1):
                dt_now = datetime.now()
                logger.info(f"Recording sample number {i} on {dt_now}")
                audio_fname = time_stamp_fnamer(dt_now) + ".wav"
                location = path.join(config["data_dir"], audio_fname)
                record_audio(
                    location,
                   config["sample_duration_sec"],
                    config["file_format"],
                    config["resolution"],
                    config["sampling_rate"],
                )
                locations.append(location)

                if i % num_subsamples == 0: # estimating rainfall
                    mm_hat = estimate_rainfall(infer_model, locations)
                    # logger.info("Estimated rainfall: ", mm_hat)
                    locations.clear()
                    moisture = read_moisture_sensor(channel=0, gain=1) # reading moisture sensor
                    result_data.append(
                        {
                            "time_stamp": dt_now,
                            "rainfall_estimate": mm_hat,
                            "moisture": moisture,
                        }
                    )
                    write_rain_data_to_csv(
                        result_data, config["log_dir"], config["rain_log_filename"]
                    )
                    rain += mm_hat
                    db_counter += 1

                    # reading battery parameters
                    # solar_V, battery_V, solar_I, battery_I = 17.2, 15.2, 1.5, 2.2
                    solar_V, battery_V, solar_I, battery_I = (preprocess_dataframe(ser))
                    
                    # sending data to DB
                    if db_counter == DB_write_interval:
                        if moisture and moisture < moisture_threshold and rain >= min_threshold:
                            send_data(config, mm_hat, solar_V, battery_V, solar_I, battery_I)

                        else:
                            send_data(config, 0.0, solar_V, battery_V, solar_I, battery_I)
                        rain, db_counter = 0, 0
                log_time_remaining(logger, end_time)
            logger.info(f"Finished data logging at {datetime.now()}\n")

    except KeyboardInterrupt:
        print("Execution interrupted by user")
    finally:
        pass


if __name__ == "__main__":
    main()
