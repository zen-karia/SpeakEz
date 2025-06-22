import serial
import time
import pandas as pd
import os

# === CONFIGURATION ===
COM_PORT = 'COM3'             # Replace with your actual port
BAUD_RATE = 115200
DURATION = 2.0                # seconds
SAMPLE_RATE = 20             # Hz
DATA_FILE = 'all_data.csv'

# === SETUP ===
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
print(f"[Connected] Listening on {COM_PORT} at {BAUD_RATE} baud.")

# Get user label once
while True:
    letter = input("Enter the letter you're recording: ").strip().upper()
    if len(letter) == 1 and letter.isalpha():
        break
    else:
        print("Please enter a single alphabetical letter (A-Z).")

# Initialize sample_id
if os.path.exists(DATA_FILE):
    existing_data = pd.read_csv(DATA_FILE)
    sample_id = existing_data['sample_id'].max() + 1
else:
    with open(DATA_FILE, 'w') as f:
        f.write('flex1,flex2,flex3,flex4,flex5,label,sample_id\n')
    sample_id = 0

# === MAIN LOOP: Wait for data stream repeatedly ===
try:
    print(f"Ready to record letter '{letter}'. Press the button on your glove to start recording.")

    last_record_time = 0  # Track time of last capture

    while True:
        if ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()

            # Only proceed if enough time has passed since last recording
            if time.time() - last_record_time < 2.5:
                continue  # skip any leftover data too soon

            # Start only if valid flex data
            parts = line.split(',')
            if len(parts) == 5:
                try:
                    float_parts = [float(x) for x in parts]
                except ValueError:
                    continue

                # Begin Recording
                print(f"[Recording] Sample #{sample_id} started...")
                data = [float_parts]
                start_time = time.time()

                while time.time() - start_time < DURATION:
                    if ser.in_waiting:
                        line = ser.readline().decode(errors='ignore').strip()
                        parts = line.split(',')
                        if len(parts) == 5:
                            try:
                                data.append([float(x) for x in parts])
                            except ValueError:
                                continue
                    time.sleep(1 / SAMPLE_RATE)

                # Save to CSV
                df = pd.DataFrame(data, columns=[f'flex{i+1}' for i in range(5)])
                df['label'] = letter
                df['sample_id'] = sample_id
                df.to_csv(DATA_FILE, mode='a', header=False, index=False)

                print(f"[Saved] Sample #{sample_id} ({len(df)} rows) for letter '{letter}'.")
                sample_id += 1
                last_record_time = time.time()

                # Clear buffer to prevent immediate false trigger
                ser.reset_input_buffer()
                print("Waiting for next button press...\n")

except KeyboardInterrupt:
    print("Program interrupted by user. Exiting.")

finally:
    ser.close()
    print("Serial port closed.")
