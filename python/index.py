import numpy as np
import io
import orthanc
import json
import base64

from mosaic import MosaicGenerator
from mip import MIPGenerator
from create_dicom_video import CreateDicomVideo

from pydicom.filebase import DicomFileLike
from pydicom import Dataset, FileDataset, dcmwrite

from typing import BinaryIO

def get_nparray(series: str):
    response = orthanc.RestApiGet( f'/series/{series}/numpy?rescale=true')
    c = np.load(io.BytesIO(response), allow_pickle=True)
    if (response.status_code != 200):
        raise Exception('Orthanc request failed')
    return c

def get_param(param, default, **request):
    try:
        return int(request['get'][param])
    except:
        return default

def displayGif(output, uri, **request):
    if request['method'] == 'GET':
        frames = get_param('frames', 30, **request)
        delay = get_param('delay', 50, **request)
        series = uri.split('/')[2]

        try:
            np_array = get_nparray(series)
            if(len(np_array.shape) != 4) :
                output.AnswerBuffer('Images are not 3D', 'text/plain')
                return
            gifBuffer = MIPGenerator(np_array, frames, delay, 360)
            memory_output = io.BytesIO()
            gifBuffer.create_gif(memory_output)
            memory_output.seek(0)
            output.AnswerBuffer(memory_output.read(), 'image/gif')
        except Exception as e:
            #Load unsuported.png image
            with open('/python/unsupported.png', 'rb') as f:
                output.AnswerBuffer(f.read(), 'image/png')
    else:
        output.SendMethodNotAllowed('GET')

def displayMosaic(output, uri, **request):
    if request['method'] == 'GET':
        cols = get_param('cols', 5, **request)
        nb_images = get_param('images', 20, **request)
        finalWidth = get_param('width', 512, **request)
        finalHeight = get_param('height', 512, **request)
        series = uri.split('/')[2]
        try:
            np_array = get_nparray(series)
            mosaicBuffer = MosaicGenerator(np_array, cols, nb_images, finalWidth, finalHeight)
            memory_output = io.BytesIO()
            mosaicBuffer.createImage(memory_output)
            memory_output.seek(0)
            output.AnswerBuffer(memory_output.read(), 'image/png')
        except Exception as e:
            with open('unsuported.png', 'rb') as f:
                output.AnswerBuffer(f.read(), 'image/png')
    else:
        output.SendMethodNotAllowed('GET')
        
def videoToOrthanc(output, uri: str, **request) -> None:
    body = json.loads(request['body'].decode('utf-8'))
    if request['method'] == 'POST':
        try:
            byte = base64.b64decode(body['Content'])
            fileDataset = CreateDicomVideo(byte).create_dicom(body.get('Parent', None), body.get('Tags', {})).fileDataset
            
            with io.BytesIO() as f:
                dcmwrite(f, fileDataset, write_like_original=False)
                f.seek(0)
                r = orthanc.RestApiPost(f'/instances', f.read())            
            output.AnswerBuffer(r.decode('utf-8'), 'application/json')
        except Exception as e:
            print('Error:', e)
            output.AnswerBuffer(str(e), 'text/plain')
    else:
        output.SendMethodNotAllowed('POST')
    


# def displayBugReproduction(output, uri, **request):
#     if request['method'] == 'GET':
#         try:
#             squared_list = BugReproduction().bug_reproduction()
#             output.AnswerBuffer(str(squared_list), 'text/plain')
#         except Exception as e:
#             output.AnswerBuffer(str(e), 'text/plain')
#     else:
#         output.SendMethodNotAllowed('GET')

# orthanc.RegisterRestCallback('/bug_test', displayBugReproduction)

orthanc.RegisterRestCallback('/series/(.*)/mosaic', displayMosaic)
orthanc.RegisterRestCallback('/series/(.*)/mip', displayGif)
orthanc.RegisterRestCallback('/video_test', videoToOrthanc)