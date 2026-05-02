import subprocess
import os
import shutil

# Configuration
target_script = "v3_tcp.py"
log_files = ["experiment_log.txt", "iperf.txt", "ping_log.txt", "tcp_server.txt"]
iterations = 100

def run_experiments():
    for i in range(1, iterations + 1):
        print(f"--- Starting Iteration {i}/{iterations} ---")
        
        # 1. Run the script
        # Using subprocess.run waits for the script to finish before continuing
        try:
            subprocess.run(["python", target_script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during iteration {i}: {e}")
            continue

        # 2. Create the destination folder
        folder_name = f"iteration_{i}"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # 3. Move the generated files
        for file_name in log_files:
            if os.path.exists(file_name):
                # Using move will overwrite if necessary or simply transfer
                shutil.move(file_name, os.path.join(folder_name, file_name))
            else:
                print(f"Warning: {file_name} was not found after iteration {i}.")

    print("\nAll 100 iterations complete.")

if __name__ == "__main__":
    run_experiments()
