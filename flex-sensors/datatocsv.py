import serial
import time
import pandas as pd
import os

# Config
COM_PORT = 'COM3'
BAUD_RATE = 115200
DURATION = 2.0
SAMPLE_RATE = 20
DATA_FILE = 'all_data.csv'

# Set up serial
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
print(f"Listening on {COM_PORT}...")

# Initialize sample_id
if os.path.exists(DATA_FILE):
    df_existing = pd.read_csv(DATA_FILE)
    sample_id = df_existing['sample_id'].max() + 1
else:
    with open(DATA_FILE, 'w') as f:
        f.write('flex1,flex2,flex3,flex4,flex5,label,sample_id\n')
    sample_id = 0

def record_flex_data(label):
    global sample_id
    data = []
    print(f"Recording for letter '{label}' (sample #{sample_id})...")

    start_time = time.time()
    while time.time() - start_time < DURATION:
        if ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            if line == "DONE":
                break
            parts = line.split(',')
            if len(parts) == 5:
                try:
                    row = [float(x) for x in parts]
                    row += [label, sample_id]
                    data.append(row)
                except ValueError:
                    continue
        time.sleep(1 / SAMPLE_RATE)

    df = pd.DataFrame(data, columns=['flex1', 'flex2', 'flex3', 'flex4', 'flex5', 'label', 'sample_id'])
    df.to_csv(DATA_FILE, mode='a', header=False, index=False)
    print(f"Saved {len(df)} rows for '{label}' (sample_id {sample_id}).\n")
    sample_id += 1

# Main Loop
try:
    while True:
        letter = input("Enter the letter you're recording: ").strip().upper()
        if not (len(letter) == 1 and letter.isalpha()):
            print("Invalid input. Try again.")
            continue
        print(f"Now press the glove button to record letter '{letter}'...")
        
        # Wait for data stream to begin
        while True:
            if ser.in_waiting:
                first_line = ser.readline().decode(errors='ignore').strip()
                if len(first_line.split(',')) == 5:
                    print("Data stream detected. Starting capture.")
                    data_row = [float(x) for x in first_line.split(',')]
                    break
        
        # Include first line and then continue capture
        record_flex_data(letter)
except KeyboardInterrupt:
    print("Exiting.")
finally:
    ser.close()
