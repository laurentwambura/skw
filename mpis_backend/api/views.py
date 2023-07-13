from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from django.db import connection
from mpis_backend.api import serializers
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView
from mpis_backend import models
from django.http import JsonResponse
from mpis_backend.api import utils
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .my_utils import get_sekta


class CreateMaoniAPIView(ListCreateAPIView):
    queryset = models.Maoni.objects.all()
    serializer_class = serializers.MaoniSerializer


class CheckMkoaAPIView(RetrieveAPIView):
    queryset = models.Jimbo.objects.all()

    def get(self, request, *args, **kwargs):
        if self.queryset.filter(mkoa=self.kwargs.get('mkoa')):
            result = {
                'jibu': True
            }
            return JsonResponse(result)
        else:
            result = {
                'jibu': False
            }
            return JsonResponse(result)


# class CreateMaoniAPIView(ListCreateAPIView):
#     queryset = models.Maoni.objects.all()
#     serializer_class = serializers.MaoniSerializer


class CheckJimboAPIView(RetrieveAPIView):
    queryset = models.Jimbo.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.queryset.filter(mkoa=self.kwargs.get('mkoa'))
        if queryset.filter(id=self.kwargs.get('jimbo')):
            result = {
                'jibu': True
            }
            return JsonResponse(result)
        else:
            result = {
                'jibu': False
            }
            return JsonResponse(result)


class CheckSektaAPIView(RetrieveAPIView):
    queryset = models.Sekta.objects.all()

    def get(self, request, *args, **kwargs):
        if self.queryset.filter(jina=self.kwargs.get('jina')):
            result = {
                'jibu': True
            }
            return JsonResponse(result)
        else:
            result = {
                'jibu': False
            }
            return JsonResponse(result)


class SektaListAPIView(ListAPIView):
    queryset = models.Sekta.objects.all()

    def get(self, request, *args, **kwargs):
        m = self.queryset.all()
        serializer = serializers.SektaSerializer(m, many=True)
        sekta = utils.get_sekta(serializer.data)
        result = {'sekta': sekta}
        return JsonResponse(result)


class JimboListAPIView(ListAPIView):
    queryset = models.Jimbo.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.queryset.filter(mkoa=self.kwargs.get('mkoa'))
        serializer = serializers.JimboSerializer(queryset, many=True)
        majimbo = utils.get_majimbo(serializer.data)
        result = {'majimbo': majimbo}
        return JsonResponse(result)


def get_feedback(request, uname):
    # print(request.method)
    if request.method == 'GET':
        try:
            user = models.User.objects.get(username=uname)
        except models.User.DoesNotExist:
            result = {'error': 'username does not exist'}
            return JsonResponse(result)
        mbunge = models.RC.objects.get(user=user)
        jimbo = mbunge.region
        majimbo = models.Jimbo.objects.filter(mkoa=jimbo).values('id')
        print(majimbo)
        maoni = models.Maoni.objects.filter(jimbo_id__in=majimbo)  # you can also use Subquery()
        serializer = serializers.MaoniSerializer(maoni, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        result = {'error': 'send get request'}
        return JsonResponse(result)


# @api_view(['POST', 'GET'])
# def create_user(request):
#     if request.method == 'POST':
#         print(request.data['username'])
#         print(request.data['passwd1'])
#         print(request.data['passwd2'])
#         return HttpResponse('thanks')


@api_view(['GET'])
def get_regions(request):
    if request.method == 'GET':
        regions = set(models.Jimbo.objects.values_list('mkoa', flat=True))
        result = {'regions': list(regions)}
        return JsonResponse(result)
    else:
        pass


class CreateRegionCommissioner(APIView):
    permission_classes = (IsAuthenticated,)

    # def get(self, request):
    #     pass

    def post(self, request):
        data = request.data
        print(data)
        rc_serializer = serializers.UserSerializer(data=data)
        if rc_serializer.is_valid():
            rc_serializer.save()
            uid = models.User.objects.get(username=data['username'])
            generated_token = Token.objects.get(user_id=uid)
            content = {
                'generated_token': generated_token.key
            }
            return Response(content, status=status.HTTP_201_CREATED)
        return Response(rc_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MajimboListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.Jimbo.objects.all()

    def get(self, request, *args, **kwargs):
        if not request.user.is_admin:
            rc = models.RC.objects.get(user__username=request.user.username)
            print(rc.region)
            queryset = list(self.queryset.filter(mkoa=rc.region).values('id', 'jina_la_jimbo'))
            # serializer = serializers.JimboSerializer(queryset, many=True)
            # majimbo = utils.get_majimbo(serializer.data)
            result = {'majimbo': queryset}
            return Response(result)
        else:
            result = {'result': 'user is not RC'}
            return Response(result)


@api_view(['GET'])
def get_sectors(request):
    if request.method == 'GET':
        sectors = models.Sekta.objects.values('id', 'jina')
        result = {'sectors': sectors}
        return Response(result)
    else:
        pass


# @method_decorator(csrf_exempt, name='dispatch')
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_admin:
            rc = models.RC.objects.get(user__username=user.username)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'role': 'rc',
                'region': rc.region
            })
        else:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'role': 'admin'
            })


class ReportListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    # queryset = models.Jimbo.objects.all()
    maoni = None

    def get(self, request, *args, **kwargs):
        # print(request.method)
        try:
            user = models.User.objects.get(username=request.user.username)
        except models.User.DoesNotExist:
            result = {'error': 'username does not exist'}
            return Response(result)
        if not request.user.is_admin:
            mbunge = models.RC.objects.get(user=user)
            jimbo = mbunge.region
            majimbo = models.Jimbo.objects.filter(mkoa=jimbo).values('id')
            # print(list(models.Jimbo.objects.filter(mkoa=jimbo).values_list('id',flat=True)))
            maoni = models.Maoni.objects.filter(jimbo_id__in=majimbo)  # you can also use Subquery()
            return Response(self.get_summary_report(maoni))
            # serializer = serializers.MaoniSerializer(maoni, many=True)
            # return JsonResponse(serializer.data, safe=False)
        else:
            result = {'error': 'user is not RC'}
            return Response(result)

    def get_summary_report(self, maoni):
        response = dict()
        if maoni:
            for oni in maoni:
                category = self.get_category(oni)
                jimbo = oni.jimbo.jina_la_jimbo
                sekta = oni.sekta.jina
                if jimbo in response:
                    if sekta in response[jimbo]:
                        if category in response[jimbo][sekta]:
                            response[jimbo][sekta][category] += 1
                        else:
                            response[jimbo][sekta][category] = 1
                    else:
                        cat1 = dict()
                        cat1[category] = 1
                        response[jimbo][sekta] = cat1
                else:
                    cat_2 = dict()
                    cat_2[category] = 1
                    sekta_1 = dict()
                    sekta_1[sekta] = cat_2
                    response[jimbo] = sekta_1
            print(response)
            return response
        else:
            print('Hakuna maoni')
            return {'response': 'no suggestions for this user'}

    def get_category(self, oni):
        if int(oni.category) == 1:
            return 'Pongezi'
        elif int(oni.category) == 2:
            return 'Kosoa'
        else:
            return 'Maoni'


class SummaryListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    def my_custom_sql(self, majimbo):
        sql = f'''
        select JINA_LA_JIMBO,JINA,FEEDBACK_TYPE,count(*) COUNT
        from
        (
        select maoni,jina_la_jimbo,mkoa,jina,CASE category
        WHEN 1 THEN 'Pongezi'
        WHEN 2 THEN 'Kosoa'
        ELSE 'Maoni'
        END FEEDBACK_TYPE
        from mpis_backend_maoni m inner join mpis_backend_jimbo j on m.jimbo_id = j.id
        inner join mpis_backend_sekta s on m.sekta_id = s.id
        where j.id in {majimbo}
        ) i
        group by jina_la_jimbo,jina,FEEDBACK_TYPE '''
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchall()
        return row

    def get(self, request, *args, **kwargs):
        try:
            user = models.User.objects.get(username=request.user.username)
        except models.User.DoesNotExist:
            result = {'error': 'username does not exist'}
            return Response(result)
        if not request.user.is_admin:
            mbunge = models.RC.objects.get(user=user)
            jimbo = mbunge.region
            majimbo = tuple(models.Jimbo.objects.filter(mkoa=jimbo).values_list('id', flat=True))
            print(majimbo)
            records = self.my_custom_sql(majimbo)
            return Response(self.get_summary(records))
        else:
            result = {'error': 'user is not RC'}
            return Response(result)

    def get_summary(self, data):
        response = {'majimbo': []}
        for data in data:
            if any(d.get('name') == data[0] for d in response['majimbo']):
                for jimbo in response['majimbo']:
                    if jimbo['name'] == data[0]:
                        for sekta in jimbo['sekta']:
                            if sekta['name'] == data[1]:
                                sekta[data[2]] = data[3]
                        jimbo[data[2] + '_Total'] += data[3]
            else:
                jimbo = {
                    'name': data[0],
                    'sekta': get_sekta(),
                    'Pongezi_Total': 0,
                    'Kosoa_Total': 0,
                    'Maoni_Total': 0,
                }
                for sekta in jimbo['sekta']:
                    if sekta['name'] == data[1]:
                        sekta[data[2]] = data[3]
                jimbo[data[2] + '_Total'] += data[3]
                response['majimbo'].append(jimbo)
        return response


class FeedbackListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    def my_custom_sql(self,majimbo):
        sql = f'''
        select mkoa,jina_la_jimbo,jina as sekta,maoni,status,CASE category
        WHEN 1 THEN 'Pongezi'
        WHEN 2 THEN 'Kosoa'
        ELSE 'Maoni'
        END FEEDBACK_TYPE
        from mpis_backend_maoni m inner join mpis_backend_jimbo j on m.jimbo_id = j.id
        inner join mpis_backend_sekta s on m.sekta_id = s.id
        where j.id in {majimbo} '''
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchall()
        return row
    def get(self, request, *args, **kwargs):
        try:
            user = models.User.objects.get(username=request.user.username)
        except models.User.DoesNotExist:
            result = {'error': 'username does not exist'}
            return Response(result)
        if not request.user.is_admin:
            mbunge = models.RC.objects.get(user=user)
            jimbo = mbunge.region
            majimbo = tuple(models.Jimbo.objects.filter(mkoa=jimbo).values_list('id', flat=True))
            print(majimbo)
            maoni = self.my_custom_sql(majimbo)
            result = list()
            for oni in maoni:
                oni_dict = dict()
                oni_dict['mkoa'] = oni[0]
                oni_dict['jimbo'] = oni[1]
                oni_dict['sekta'] = oni[2]
                oni_dict['maoni'] = oni[3]
                oni_dict['status'] = oni[4]
                oni_dict['feedback_type'] = oni[5]
                result.append(oni_dict)
            result = {'result': result}
            return Response(result)
        else:
            result = {'error': 'user is not RC'}
            return Response(result)
           