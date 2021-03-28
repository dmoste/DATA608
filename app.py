import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
    '$select=distinct spc_common').replace(' ', '%20')
all_trees = pd.read_json(soql_url)

app = dash.Dash(__name__)

boroughs = ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']
species = all_trees['spc_common'].values.tolist()

app.layout = html.Div(children=[
    html.H1(children='Trees'),

    html.Div(children='''
        An exploration of tree health in NYC
    '''),
    
    dcc.Dropdown(
        id='borough',
        options=[{'label': i, 'value': i} for i in boroughs],
        value = 'Bronx'
    ),
    
    dcc.Dropdown(
        id='species',
        options=[{'label': i, 'value': i} for i in species],
        value = 'cherry'
    ),
    
    dcc.RadioItems(
        id='steward',
        options=[{'label': i, 'value': i} for i in ['All Data', 'Steward Trend']],
        value='All Data',
        labelStyle={'display': 'inline-block'}
    ),

    dcc.Graph(
        id='health_graph'
    )
])
             
@app.callback(
    Output('health_graph', 'figure'),
    Input('borough', 'value'),
    Input('steward', 'value'),
    Input('species', 'value'))

def update_graph(borough,steward,species):
    if steward == 'All Data':
        soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
            '$select=health,count(tree_id)' +\
            '&$where=boroname=\'' + borough + '\'&spc_common=\'' + species + '\'' +\
            '&$group=health').replace(' ', '%20')
            
        trees = pd.read_json(soql_url)
        
        tot = trees.sum(axis = 0, skipna = True)
    
        trees['count_tree_id'] = trees['count_tree_id']/tot['count_tree_id']*100
        trees['health'] = trees['health'].fillna('No Record')
        
        fig = px.bar(trees, x = 'health', y = 'count_tree_id', barmode = 'group',
                     category_orders = {'health':['Good','Fair','Poor']},
                     labels = dict(health = "Tree Health",
                                   count_tree_id = "# of Trees"))
        fig.update_yaxes(range = [0, 100])
    else:
        trees = pd.DataFrame()
        steward_care = ['None','1or2','3or4','4orMore']
        for level in steward_care:
            soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
                '$select=health,count(tree_id)' +\
                '&$where=boroname=\'' + borough + '\'&spc_common=\'' + species + '\'&steward=\'' + level + '\'' +\
                '&$group=health').replace(' ', '%20')
                
            df = pd.read_json(soql_url)
            tot = df.sum(axis = 0, skipna = True)
            df['count_tree_id'] = df['count_tree_id']/tot[1]*100
            df['steward'] = level
            
            trees = pd.concat([trees,df])
        
        fig = px.bar(trees, x = 'steward', y = 'count_tree_id', color = 'health', barmode = 'stack',
                     category_orders = {'steward':['None','1or2','3or4','4orMore'],
                                        'health':['Good','Fair','Poor']},
                     labels = dict(steward = "Steward Status",
                                   count_tree_id = "# of Trees",
                                   health = "Tree Health"))

    return fig

if __name__ == '__main__':
    app.run_server(debug=False)