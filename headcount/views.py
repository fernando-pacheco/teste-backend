from django.db.models import Count, F
from django.db.models.functions import ExtractYear, ExtractMonth
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializer import HeadcountSerializer
from .models import Headcount

class HeadcountViewSet(viewsets.ModelViewSet):
    '''Viewset para a tabela headcount
    -
    Retorna todos os registros da tabela headcount pelo endpoint /headcount/'''
    queryset = Headcount.objects.all()
    serializer_class = HeadcountSerializer
    http_method_names = ['get']

    @action(detail=False, methods=['get'], url_path='line_chart')
    def line_chart(self, request):
        '''Retorna um JSON com os dados para o gráfico de linha
        -
        endpoint /headcount/line_chart
        - Como parâmetro de entrada:
           - init_date: data inicial da base
           - end_date: data final da base
        '''
        # Pega todos os registros com fg_status igual a 1
        queryset = Headcount.objects.filter(fg_status=1)

        # Cria os dados para o gráfico separando por ano, mês e contagem
        data = queryset.annotate(
            year=ExtractYear('dt_reference_month'),
            month=ExtractMonth('dt_reference_month'),
        ).values('year', 'month').annotate(
            headcount=Count('id_employee', filter=F('fg_status') == 1),
        ).values('year', 'month', 'headcount')

        # Serializa o retorno dos dados
        response_data = {
            "xAxis": {
                "type": "category",
                "data": [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec"
                ]
            },
            "yAxis": {
                "type": "value"
            },
            "series": {
                "type": "stacked_line",
                "series": []
            },
            "title": "Headcount por Ano",
            "grid": 6,
            "color": [
                "#D4DDE2",
                "#A3B6C2"
            ]
        }

        # Separando os dados por ano e inserindo na serie
        for entrada in data:
            year = entrada['year']
            count = entrada['headcount']

            # Encontra e agrupa os valores na serie para o ano escolhido, se não houver -> None
            series_data = next((s for s in response_data['series']['series'] if s['name'] == str(year)), None)

            # Cria uma nova serie['data'] com 12 elementos nulos se não houver e adiciona a serie
            if series_data is None:
                series_data = {
                    "name": str(year),
                    "type": "line",
                    "data": [0] * 12
                }
                response_data['series']['series'].append(series_data)

            # Adiciona o valor na serie correspondente ao mês
            series_data['data'][entrada['month'] - 1] = count

        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='category_charts')
    def category_charts(self, request):
        '''Retorna um JSON com os dados para o gráfico de categoria
        -
        endpoint /headcount/category_charts
        - Como parâmetro de entrada:
           - init_date: data inicial da base
           - end_date: data final da base
           - category_1: Empresa
        '''
        # Pega todos os registros com fg_status igual a 1
        queryset = Headcount.objects.filter(fg_status=1)
        
        # Cria os dados para o gráfico separando por ano, empresa e contagem
        data = queryset.annotate(
            year=ExtractYear('dt_reference_month'),
            month=ExtractMonth('dt_reference_month'),
        ).values('year', 'ds_category_1').annotate(
            count=Count('id_employee', filter=F('fg_status') == 1),
        ).values('year', 'ds_category_1', 'count')

        # Serializa o retorno dos dados
        response_data = {
            "xAxis": {
                "type": "value",
                "show": True,
                "max": {}
            },
            "yAxis": {
                "type": "category",
                "data": []
            },
            "series": {
                "type": "horizontal_stacked",
                "series": [
                    {
                        "name": "Colaboradores",
                        "data": [],
                        "type": "bar"
                    }
                ]
            },
            "title": "Empresa",
            "grid": 6,
            "color": ["#2896DC"],
            "is_percent": False
        }

        # Criando a serie
        category_data = {}
        
        # Encontra e agrupa os valores na serie para o ano escolhido, se não houver -> None
        for entrada in data:
            category = entrada['ds_category_1']
            count = entrada['count']
            
            # Caso não exista, cria uma categoria sem dados
            if category not in category_data:
                category_data[category] = []
            
            # Adiciona o valor na serie correspondente
            category_data[category].append(count)

        # Preenche os dados com os nomes das Empresas
        response_data['yAxis']['data'] = list(category_data.keys())

        # Preenche os dados com as quantidades de colaboradores cujo o fg_status = 1
        response_data['series']['series'][0]['data'] = [sum(category_data[category]) for category in response_data['yAxis']['data']]

        return Response(response_data, status=status.HTTP_200_OK)