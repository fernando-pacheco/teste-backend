# turnover/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from .models import Turnover
from .serializer import TurnoverSerializer, TurnoverCategoryChartSerializer, TurnoverLineChartSerializer

class TurnoverViewSet(viewsets.ModelViewSet):
    '''Retorna os dados para o gráfico de linha e categoria
    -
    Retorna todos os registros da tabela turnover pelo endpoint /turnover/'''
    queryset = Turnover.objects.all()
    serializer_class = TurnoverSerializer
    http_method_names = ['get']

    @action(detail=False, methods=['get'], url_path='line_chart')
    def line_chart(self, request):
        '''Retorna um JSON com os dados para o gráfico de linha
        -
        endpoint /turnover/line_chart
        - Como parâmetro de entrada:
           - init_date: data inicial da base
           - end_date: data final da base
        '''
        # Instancia o serializer com os parâmetros de entrada
        serializer = TurnoverLineChartSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True) # verificação necessária, caso contrário o código quebra

        # Receber os parâmetros da URL /?init_date=yyyy-mm-dd&end_date=yyyy-mm-dd
        init_date = serializer.validated_data['init_date']
        end_date = serializer.validated_data['end_date']

        # Cria os dados para o gráfico separando por ano, mês, total de demissões e funcionários ativos 
        # para a realização dos calculos
        turnover_data = Turnover.objects.filter(
            dt_reference_month__range=[init_date, end_date],
            fg_status=1  # Filtrar apenas funcionários ativos dentro do range de datas
        ).annotate(
            year=ExtractYear('dt_reference_month'),
            month=ExtractMonth('dt_reference_month'),
        ).values('year', 'month').annotate(
            total_dismissals=Sum('fg_dismissal_on_month'), # Total de demissões
            active_employees=Count('id_employee'), # Funcionários ativos
        ).values('year', 'month', 'total_dismissals', 'active_employees')

        # Serializa o retorno dos dados
        response_data = {
            "xAxis": {
                "type": "category",
                "data": [
                    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                ]
            },
            "yAxis": {
                "type": "value"
            },
            "series": {
                "type": "stacked_line",
                "series": []
            },
            "title": "Taxa de Turnover por Ano (%)",
            "grid": 6,
            "color": ["#D4DDE2", "#A3B6C2"]
        }

        # Separando os dados por ano, mês, total de demissões e funcionários ativos e inserindo na serie
        for entrada in turnover_data:
            year = entrada['year']
            month = entrada['month']
            total_dismissals = entrada['total_dismissals']
            active_employees = entrada['active_employees']

            # Calcular a taxa de turnover fazendo a verificação de CE
            if active_employees > 0:
                turnover_rate = (total_dismissals / active_employees) * 100
            else:
                turnover_rate = 0

            # Adicionar os dados ao gráfico
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
            series_data['data'][month - 1] = round(turnover_rate, 2)

        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='category_chart')
    def category_charts(self, request):
        '''Retorna um JSON com os dados para o gráfico de categoria
        -
        endpoint /headcount/category_charts
        - Como parâmetro de entrada:
           - init_date: data inicial da base
           - end_date: data final da base
           - category_1: Empresa
        '''
        
        # Instancia o serializer com os parâmetros de entrada
        serializer = TurnoverCategoryChartSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # Receber os parâmetros da URL /?init_date=yyyy-mm-dd&end_date=yyyy-mm-dd&category=ds_category_1
        init_date = serializer.validated_data['init_date']
        end_date = serializer.validated_data['end_date']
        category = serializer.validated_data['category']

        # Calcular a quantidade de meses no período do filtro -> período
        filter_month_count = (end_date.year - init_date.year) * 12 + (end_date.month - init_date.month) + 1


        # Calcular a taxa de turnover por categoria para os gráficos
        turnover_data = Turnover.objects.filter(
            dt_reference_month__range=[init_date, end_date],
            ds_category_1=category
        ).annotate(
            total_dismissals=Sum('fg_dismissal_on_month'),
            active_employees=Sum('fg_status'),
        ).values('ds_category_5').annotate( # Faz uma separação por função sendo exercida na empresa
            turnover_rate = F('total_dismissals') / F('active_employees') * 100 / filter_month_count 
        ).values('ds_category_5', 'turnover_rate') # Retorna o cálculo feito e função

        # Serializa o retorno dos dados
        response_data = {
            "xAxis": {
                "type": "value",
                "show": True,
                "max": {}
            },
            "yAxis": {
                "type": "category",
                "data": list(turnover_data.values_list('ds_category_5', flat=True)) # Dinamiza a exibição dos dados
            },
            "series": {
                "type": "horizontal_stacked",
                "series": [
                    {
                        "name": "Colaboradores",
                        "data": list(turnover_data.values_list('turnover_rate', flat=True)), # Dinamiza a exibição dos dados
                        "type": "bar"
                    }
                ]
            },
            "title": "Empresa",
            "grid": 6,
            "color": ["#2896DC"],
            "is%": False
        }

        return Response(turnover_data, status=status.HTTP_200_OK)
