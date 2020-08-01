import datetime
import os
import sys
import time

from sanic import Sanic
from sanic.response import json, file

from src.controllers.image_controller import ImageController

# Setup application
app = Sanic(name='test-fastapi')

# return JSON
ret = dict()

@app.route('/', methods=['GET', 'OPTIONS'])
async def option(request):
    return json(
        {'success': True},
        headers={
            'Access-Control-Allow-Headers': 'api_key, Content-Type',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Hostname': HOST_NAME,
            'X-FPTAI-BILLING': 0
        })

@app.route('/', methods=['POST'])
async def read_api(request):
    print('Started new at: ' + str(datetime.datetime.now()))
    response_status = 200

    img_controller = ImageController()

    try:
        if 'image' in request.files:
            image = request.files.get('image')
            data_type = 'image'
            result = img_controller.image2text(image, data_type)
            print(result)
        else:
            result['error'] = 'Invalid Parameters or Values!'

        if 'error' in result:
            fptai_billing = 0
            response_status = 400
            if result['error'] == 'Invalid Parameters or Values!':
                ret['errorCode'] = 1
                ret['errorMessage'] = result['error']
                ret['data'] = []
            elif result['error'] == 'Please upload only 2 images in the list':
                ret['errorCode'] = 2
                ret['errorMessage'] = result['error']
                ret['data'] = []
            elif result['error'] == 'Unable to find ID card in the image':
                ret['errorCode'] = 3
                ret['errorMessage'] = result['error']
                ret['data'] = []
                fptai_billing = 1
            elif result['error'] == 'Downloading file timed out':
                ret['errorCode'] = 4
                ret['errorMessage'] = result['error']
                ret['data'] = []
            elif result['error'] == 'No URL in the request':
                ret['errorCode'] = 5
                ret['errorMessage'] = result['error']
                ret['data'] = []
            elif result['error'] == 'Failed to open the URL!':
                ret['errorCode'] = 6
                ret['errorMessage'] = result['error']
                ret['data'] = []
            elif result['error'] == 'Invalid image file':
                ret['errorCode'] = 7
                ret['errorMessage'] = result['error']
                ret['data'] = []
            elif result['error'] == 'Bad data':
                ret['errorCode'] = 8
                ret['errorMessage'] = result['error']
                ret['data'] = []
            elif result['error'] == 'No string base64 in the request':
                ret['errorCode'] = 9
                ret['errorMessage'] = result['error']
                ret['data'] = []
            elif result['error'] == 'String base64 is not valid':
                ret['errorCode'] = 10
                ret['errorMessage'] = result['error']
                ret['data'] = []
            else:
                ret['errorCode'] = 1
                ret['errorMessage'] = 'Invalid Parameters or Values!'
                ret['data'] = []
        else:
            ret['errorCode'] = 0
            ret['errorMessage'] = ''
            ret['data'] = []
               
        return json(ret, ensure_ascii=False, escape_forward_slashes=False,
                    headers={
                        'Access-Control-Allow-Headers': 'api_key, Content-Type',
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': '*'
                    },
                    status=response_status)
    except Exception as e:
        print(e)
        return json("Something wrong has happened",
                    headers={
                        'Access-Control-Allow-Headers': 'api_key, Content-Type',
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': '*'
                    },
                    status=500)


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', workers=1, debug=True)
