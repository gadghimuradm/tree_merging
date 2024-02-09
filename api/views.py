import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from xml.etree import ElementTree
import xmltodict
from api.utils import _decode, merge_trees, normalize_data


class MergeTreesAPIView(APIView):

    def post(self, *args, **kwargs):
        if self.request.content_type == 'application/json':
            try:
                data = json.loads(self.request.body)
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif self.request.content_type == 'application/xml':
            try:
                data = json.loads(json.dumps(xmltodict.parse(self.request.body), indent=4), object_hook=_decode)["root"]
            except ElementTree.ParseError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            data = merge_trees(data)
            normalize_data(data)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)
