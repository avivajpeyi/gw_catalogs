import os

from tqdm import tqdm

DATA_FILE = "data_files.txt"

def makedirs():
    dirs = ["data/pycbc_search", "data/ias_search", "data/lvc_search/gwtc1",
            "data/lvc_search/gwtc2", "data/bilby/gwtc1/"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def download_data():
    download_commands = open(DATA_FILE, "r").read().split('\n')
    download_commands = [f"wget -q {c}" for c in download_commands]
    for command in tqdm(download_commands, desc="Downloading LVC Event Samples"):
        os.system(command)

def main():
    makedirs()
    download_data()





if __name__ == "__main__":
    main()
