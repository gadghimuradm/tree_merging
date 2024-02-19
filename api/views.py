from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.utils import XMLTreeMerger, JSONTreeMerger


class MergeTreesAPIView(APIView):

    def post(self, *args, **kwargs):
        if self.request.content_type == 'application/json':
            data = JSONTreeMerger(self.request.body).get_tree()
        elif self.request.content_type == 'application/xml':
            data = XMLTreeMerger(self.request.body).get_tree()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)
