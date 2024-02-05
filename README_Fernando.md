# Rotas para verificação


## API Root - DRF


localhost:8000

```bash
  /headcount/
  /turnover/
```

Rotas puxam todos os dados da base dos respectivos (get_all)
## Extra_actions

No canto superior direito, é possível notar o botão extra_actions, nele direciona para as rotas

localhost:8000 -> headcount

```bash
  GET headcount/line_chart/?init_date=yyyy-mm-dd&end_date=yyyy-mm-dd                              # passando os parâmetros de filtro
  GET headcount/category_chart/?init_date=yyyy-mm-dd&end_date=yyyy-mm-dd&category=ds_category_1   # passando os parâmetros de filtro
```
e localhost:8000 -> turnover

```bash
  GET turnover/line_chart/?init_date=yyyy-mm-dd&end_date=yyyy-mm-dd                              # passando os parâmetros de filtro
  GET turnover/category_chart/?init_date=yyyy-mm-dd&end_date=yyyy-mm-dd&category=ds_category_1   # passando os parâmetros de filtro
```
