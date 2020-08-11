import datetime
import os
import time
import shutil
import logging
import traceback
import imghdr
import cv2
import whatimage
from contextlib import contextmanager
import signal
import requests

from pdf2image import convert_from_bytes

WORKING_DIR = os.path.abspath('.')
UPLOADED_DIR = WORKING_DIR + '/resources/images/original'

class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Downloading file timed out")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class ImageController:
    def __init__(self):
        self.upload_path = ''
        self.result = dict()
        self.result_face = dict()

    def image2text(self, image, data_type):
        '''
        Extract information from ID card images
        '''
        # Total processing time
        start_time = time.time()

        # Image's name with time-stamp
        try:
            if data_type == "url":
                print('image: ', image)
                filename = str(
                    datetime.datetime.now().isoformat()) + '_' + 'url.jpg'
                try:
                    with time_limit(5):
                        r = requests.get(image, allow_redirects=True)
                except TimeoutException as e:
                    logging.error("Downloading file timed out!")
                    self.result['error'] = 'Downloading file timed out'
                    return self.result
                except Exception as e:
                    logging.error('Exception: %s', e)
                    self.result['error'] = 'Failed to open the URL!'
                    return self.result
            elif data_type == "image":
                # Support receive pdf file
                if image.filename.split('.')[-1] == 'pdf':
                    # Convert pdf to image
                    img_pdf = convert_from_bytes(image.file.read())[0]
                    filename = str(datetime.datetime.now().isoformat(
                    )) + '_' + ''.join(image.filename.split('.')[:-1]) + '.jpg'
                else:
                    filename = str(
                        datetime.datetime.now().isoformat()) + '_' + image.filename
            elif data_type == "masked":
                filename = str(datetime.datetime.now().isoformat()
                               ) + '_masked' + '.jpg'
            else:
                filename = str(
                    datetime.datetime.now().isoformat()) + '_base64.jpg'
        except:
            logging.error(traceback.format_exc())
            self.result['error'] = 'Bad data'
            return self.result

        # Check if upload path exits
        path_original = os.path.join(
            UPLOADED_DIR, datetime.date.today().isoformat())
        if not os.path.exists(path_original):
            os.makedirs(path_original, exist_ok=True)
        # Path to the original image
        self.upload_path = os.path.join(path_original, filename)
        print(self.upload_path)

        # Save original image
        try:
            if data_type == "masked":
                cv2.imwrite(self.upload_path, image)
            else:
                with open(self.upload_path, "wb") as f:
                    if data_type == "url":
                        f.write(r.content)
                    elif data_type == "image":
                        if image.filename.split('.')[-1] == 'pdf':
                            img_pdf.save(f)
                        else:
                            f.write(image.file.read())
                    else:
                        imgdata = base64.b64decode(image)
                        f.write(imgdata)
        except:
            logging.error(traceback.format_exc())

        # Verify that the uploaded image is valid
        try:
            if imghdr.what(self.upload_path) is None:
                with open(self.upload_path, 'rb') as f:
                    data = f.read()
                image_type = whatimage.identify_image(data)
                if image_type is not None and image_type != 'heic':
                    pass
                elif image_type == 'heic' or image_type == 'HEIC':
                    destination = self.upload_path + '.jpg'
                    subprocess.call(
                        [WORKING_DIR + '/src/libs/tifig/tifig', '-p', self.upload_path, destination])
                    self.upload_path = destination
                else:   # if not, terminate the process
                    logging.info(
                        '{} is not a valid image file'.format(filename))
                    self.result['error'] = 'Invalid image file'
                    return self.result
        except IOError:
            logging.error(traceback.format_exc())
            logging.error('Cannot open {}'.format(self.upload_path))
            return self.result

        # If the uploaded image is valid, keep going
        if filename.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'ppg', 'pgm']:
            filename = filename + '.jpg'
        try:
            img_raw = cv2.imread(self.upload_path)
            img_rgb = cv2.cvtColor(img_raw, cv2.COLOR_BGR2RGB)
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        except Exception as e:
            print(e)
            print('{} is not a valid image file'.format(filename))
            self.result['error'] = 'Invalid image file'
            return self.result

        if 'error' in self.result:
            logging.info(username + ' Image ' + filename +
                         ': ' + self.result['error'])

        return self.result

