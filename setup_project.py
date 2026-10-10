import os
import urllib.request

def create_structure():
    folders = ['data', 'notebooks', 'src']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("Project folders created.")

def download_datasets():
    urls = {
        'matches.csv': 'https://raw.githubusercontent.com/Devesh26/IPL-Data-Analysis/master/matches.csv',
        'deliveries.csv': 'https://raw.githubusercontent.com/Devesh26/IPL-Data-Analysis/master/deliveries.csv'
    }
    
    for filename, url in urls.items():
        filepath = os.path.join('data', filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename}...")
            try:
                urllib.request.urlretrieve(url, filepath)
                print(f"Downloaded {filename} successfully.")
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
        else:
            print(f"{filename} already exists.")

if __name__ == '__main__':
    create_structure()
    download_datasets()
