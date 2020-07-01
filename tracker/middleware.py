from django.http import QueryDict
import json

class DataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if request.body:
            deserialized = QueryDict(self.query_string(json.loads(request.body)))
        else:
            deserialized = QueryDict()

        if request.method.upper() == 'GET':
            request.GET_QD = request.GET.copy()
        elif request.method.upper() == 'POST':
            request.POST_QD = deserialized
        elif request.method.upper() == 'PUT':
            request.PUT_QD = deserialized
        elif request.method.upper() == 'DELETE':
            request.DELETE_QD = deserialized

        response = self.get_response(request)

        return response

    def query_string(self, dataDict):
        string = ''
        print(dataDict)
        for key in dataDict:
            if type(dataDict[key]) == list:
                for element in dataDict[key]:
                    string += "&{key}={value}".format(key=key, value=element)
            else:
                string += '&{key}={value}'.format(key=key, value=dataDict[key])

        return string.lstrip('&')
