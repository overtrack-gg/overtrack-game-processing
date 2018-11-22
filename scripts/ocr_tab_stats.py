import json
import logging
import base64

import numpy as np
import requests
import cv2
import glob
from pprint import pprint

from overtrack.util import imageops

logger = logging.getLogger(__name__)

BATCH_SIZE = 10
GAPI_VISION_ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
GAPI_VISION_API_KEY = 'AIzaSyAEhngTB-5nMQFfReT_WuXxO6W7r02SQD0'


def ocr_images_google(imgs):

    logger.info('Requesting GAPI OCR...')
    img_requests = []
    for img in imgs:
        # rw = max(1, np.argmax(np.sum(img, axis=(0, 2))[::-1] > 0))
        r, imgdata = cv2.imencode('.png', img)
        assert r
        img_requests.append({
            'image': {'content': base64.b64encode(imgdata).decode()},
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': 1,
            }],
            'imageContext': {
                'languageHints': ['en']
            }
        })
    request = json.dumps({'requests': img_requests}).encode()
    response = requests.post(GAPI_VISION_ENDPOINT_URL,
                             data=request,
                             params={'key': GAPI_VISION_API_KEY},
                             headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        logger.error('Got statuscode %d - %s', response.status_code, response.text)
        return None
    else:
        logger.info('Got statuscode 200')
        return response.json()


def parse_names_aws(ims):
    import boto3

    rekognition = boto3.client(
        'rekognition',
        region_name='ap-southeast-2'
    )
    r = rekognition.detect_text(Image={
        'Bytes': cv2.imencode('.png', np.vstack(ims))[1].tobytes()
    })['TextDetections']
    lines = [d for d in r if d['Type'] == 'LINE' if d['DetectedText'].isupper() and len(d['DetectedText']) > 2]
    # if len(lines) < 12:
    #     raise ValueError('Expected 12 names')
    # while len(lines) > 12:
    #     worst_index = int(np.argmin([l['Confidence'] for l in lines]))
    #     logger.info('Got %d names - removing worst (%s c=%d)', len(lines), lines[worst_index]['DetectedText'], lines[worst_index]['Confidence'])
    #     lines.pop(worst_index)
    return [
        l['DetectedText'] for l in lines
    ]


def main() -> None:
    ps = glob.glob('C:\\scratch\\tab_stats\\*.png')
    for i in range(len(ps) // BATCH_SIZE):
        batch = ps[i * BATCH_SIZE: (i + 1) * BATCH_SIZE]
        ims = [255 - imageops.otsu_mask(255 - cv2.imread(p, 0)) for p in batch]
        # ims = [cv2.imread(p, 0) for p in batch]
        cv2.imshow('ims', np.vstack(ims))
        results = [r['fullTextAnnotation']['text'].replace('\n', ' ').split() for r in ocr_images_google(ims)['responses']]
        pprint(results)
        cv2.waitKey(0)

    # for p in ps:
    #     im = cv2.imread(p, 0)
    #     cv2.imshow('ims', im)
    #     results = parse_names_aws(im)
    #     pprint(results)
    #     cv2.waitKey(0)
    #     print()


if __name__ == '__main__':
    main()
