import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import json

from app import app
from apps import config_app, kw_search_app, include_kw_app, definitions_app, query_app
import webbrowser
from threading import Timer


app.layout = dbc.Container(
    [
        dcc.Store(id="config_store", storage_type='local'),
        dcc.Store(id="kw_search", storage_type='session'),
        dcc.Store(id="include_fields", storage_type='session'),
        dcc.Store(id="defined_terms", storage_type='session'),
        dcc.Store(id='selected_terms_data', storage_type='memory'),

        html.H1('UKB Cohort Curator'),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(label="Configure", tab_id="config"),
                dbc.Tab(label="Define Terms", tab_id="definitions"),
                dbc.Tab(label="Cohort search", tab_id="query"),
                #dbc.Tab(label="Exclude fields", tab_id="exclude"),
                dbc.Tab(label="History", tab_id="results"),
            ],
            id="tabs",
            active_tab="config"
        ),
        html.Div(id="tab-content", className="p-4"),
        html.Div(id='search_logic_state', style={'display': 'none'}),

    ]
)


@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab:
        if active_tab == "config":
            return config_app.tab
        elif active_tab == "definitions":
         return definitions_app.tab
        elif active_tab == "query":
         return query_app.tab
        return html.P("Tab '{}' is not implemented...".format(active_tab))
    else:
        return config_app.tab

    #return active_tab#html.P("Click config to start")


#
#
# Handle next/previous tab buttons
#
@app.callback(
    Output("tabs", "active_tab"),
    [Input({'type': 'nav_btn', 'name': ALL}, "n_clicks")]
)
def tab_button_click_handler(values):
    ctx = dash.callback_context

    #TODO: Why not make a dictionary of the fields and automate this mapping. But I'm so lazy...
    button_map={"next_button_config":"definitions",
                "prev_button_terms": "config",
                "next_button_terms": "query",
                "prev_button_query": "definitions",
                "next_button_query": "history"
                }
    if ctx.triggered and ctx.triggered[0]['value']:
       button_id_dict_str = ctx.triggered[0]['prop_id'].split('.')[0]
       button_id_dict=json.loads(button_id_dict_str)
       return button_map[button_id_dict["name"]]

port = 8050 # default port

def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))

if __name__ == '__main__':
    #Timer(1, open_browser).start();
    app.run_server(debug=True, use_reloader=True, dev_tools_props_check=False, dev_tools_ui=True)
