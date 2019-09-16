import concurrent.futures
import math
import os
from datetime import datetime

from google.cloud import storage

executor = concurrent.futures.ThreadPoolExecutor(max_workers=None)


def upload_to_gcs(bucket, path, image, file_name):
    image.save(file_name)
    # client is not thread-safe...
    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blob = bucket.blob('{}{}'.format(path, file_name))
    blob.upload_from_filename(file_name)
    os.remove(file_name)
    return file_name


def upload(bucket, path, image):
    file_name = 'image_{}.png'.format(math.floor(datetime.utcnow().timestamp() * 1000))
    ret = executor.submit(upload_to_gcs, bucket, path, image, file_name)

    def finished(job):
        print('Upload has finished: {}'.format(job.result()))

    ret.add_done_callback(finished)
