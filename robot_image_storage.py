import os
import time
import boto3
import shutil
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# AWS Configuration
s3 = boto3.client('s3')
BUCKET_NAME = '<your_bucket_name>'

# Image directory and memory management settings
IMAGES_DIRECTORY = '<path_to_images_directory>'
MEMORY_THRESHOLD = 80  # in percentage

def upload_image_to_s3(file_path, bucket_name, object_name):
    with open(file_path, 'rb') as file:
        s3.upload_fileobj(file, bucket_name, object_name)
        print(f"Image {object_name} uploaded to S3")

def delete_uploaded_image(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"File {file_path} removed successfully")
    else:
        print(f"File {file_path} not found")

def get_used_memory_percentage():
    memory = psutil.virtual_memory()
    return memory.percent

class ImageEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.jpg') or event.src_path.endswith('.png'):
            file_name = os.path.basename(event.src_path)
            object_name = os.path.join('robot_images', file_name)

            # Upload the image to S3
            upload_image_to_s3(event.src_path, BUCKET_NAME, object_name)

            # Check memory usage and delete the uploaded image if necessary
            used_memory = get_used_memory_percentage()
            if used_memory >= MEMORY_THRESHOLD:
                delete_uploaded_image(event.src_path)

def main():
    event_handler = ImageEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=IMAGES_DIRECTORY, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
