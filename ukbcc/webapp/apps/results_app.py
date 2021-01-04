import dash
# from ukbcc.webapp.app import app
from app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import dash_table
import pandas as pd
import os
import json
from pathlib import Path
import plotly

from ukbcc import query, utils, stats

from dash.exceptions import PreventUpdate

cohort_results_out = dbc.Form(
    [
        dbc.FormGroup(
        [
            dbc.Label("Cohort Results File (path)", html_for={"type": "config_input","name":"cohort_results_outfile"}),
            dbc.Input(placeholder="Name and path of the file to write cohort results CSV to",
                                          type="text", id="cohort_results_outfile", persistence=False, style={"margin": "5px"}),
            dbc.FormText("Specify the name of the file to write cohort results to e.g cohort_results.csv", color="secondary")
        ],
        className='mr-3',
    ),
    dbc.Button(children="Save", color="success", id="save_cohort_results_btn", className="ml-auto", style={"margin":"5px", "display":"block"}),
    ],
)
# add_new_term_modal = dbc.Modal(
#                 [
#                     dbc.ModalHeader("Find fields"),
#                     dbc.ModalBody(id="find_terms_modalbody", children=kw_search_app.kw_search_group),
#                     dbc.ModalFooter(
#                         dbc.Button("Close", id={'type': 'find_terms_modal_btn', 'name': 'close'}, className="ml-auto"),
#                     id="find_terms_modalfooter"),
#                 ],
#                 id="find_terms_modal",
#                 size="xl",
#                 style={'maxWidth': '1600px', 'width': '90%'})
#

tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Cohort Search Results", className="card-text"),
            # html.P("Please find the results of your cohort search below", className="card-text"),
            dbc.Row(id='history_results', align='center'),
            html.Div([
                dbc.Button("Save", color='success', id="save_results_modal_btn", style={"margin": "5px"})
            ]),
            dbc.Row(dbc.Col(id='save_results_status'), align='center'),
            dbc.Row(dbc.Col(id='defined_term_rows')),
            html.H3("Cohort Search Results Report", className="card-text"),
            html.Div(id='history_results_report'),
            html.Div([
               dbc.Button("Previous", color='primary', id={"name":"prev_button_results","type":"nav_btn"}, style={"margin": "5px"}),
            ]),
            dbc.Modal(
                [
                    dbc.ModalHeader("Write cohort results to file"),
                    dbc.ModalBody(cohort_results_out, id="write_cohort_results_modal", style={"overflow-wrap": "break-word"}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close_cohort_results_modal_btn", className="ml-auto", style={"margin": "5px"}),
                    ),
                ],
                id="save_cohort_results_modal",
                size="lg"
            ),
        ]
    ),
    className="mt-3",
)

def get_default_fields_table():
    fields = {'Field':['Year of Birth', 'Genetic Sex'], 'FieldID':['3', '52'], 'Coding':['10', '3'], 'Value':['all','all'], 'Meaning':['all', 'all']}
    df = pd.DataFrame.from_dict(fields)
    return df

def get_default_dropdown_card():
    default_cols = {'34-0.0': 'int64', '52-0.0': 'int64', '21000-0.0': 'int64', '22001-0.0': 'float64', '22021-0.0': 'float64'}
    default_df = get_default_fields_table()
    default_card = get_dropdown_card(0, 1, f"terms {len(default_df.index)}", default_df)
    return default_card

def get_dropdown_card(idx, id, v, term_count_str, terms_tab):
    card = dbc.Card(dbc.Row(
    [
        dbc.Col(dbc.Button("❌", id={'modal_ctrl':'none','name': id + '_remove'}), width={"size": 1}),
        dbc.Col(html.H3(v['name'], id=id + '_name_title'), width={"size": 4}),
        dbc.Col(dbc.Button("Add terms", id={"name": id + '_any', "type": "find_terms_modal_btn"}),
                width={"size": 2}),

        dbc.Col(html.H5(term_count_str, id={"name": id + '_terms', "type": "text"}), width={"size": 3}),
        dbc.Col(dbc.Button("▼", id={"index": idx, "type": "expand"}), width={"size": 1, "offset":1}),
        dbc.Collapse(
            dbc.Card(
                dbc.CardBody([
                    html.H5('Defining terms'),
                    terms_tab
                ])),
            id={"index": idx, "type": "collapse"})
        ]))
    return card

def toggle_modals(n1, n2, n3, is_open):
    if n1 or n3:
        return not is_open
    return is_open

@app.callback(
    [Output("save_cohort_results_modal", "is_open"),
    Output("save_results_status", "children")],
    [Input("save_results_modal_btn", "n_clicks"),
    Input("save_cohort_results_btn", "n_clicks"),
    Input("close_cohort_results_modal_btn", "n_clicks")],
    [State("config_store","data"),
    State("cohort_id_results", "data"),
    State("cohort_results_outfile", "value"),
    State("save_cohort_results_modal", "is_open")],
)
def save_cohort_results(n1: int, n2: int, n3: int, config_init: dict, cohort: pd.DataFrame, outfilename: str, is_open: bool):
    """Handler to save cohort results to CSV file.

    Keyword arguments:
    ------------------
    n1: int
        indicates number of clicks of "save_cohort_results_modal_btn"
    n2: int
        indicates number of clicks of "save_cohort_ids_btn"
    n3: int
        indicates number of clicks of "close_cohort_file_modal_btn"
    config_init: dict
        contains configuration file paths
    cohort: pd.DataFrame
        filtered main dataset for specific cohort criteria, with columns
        determined by the selected datafields
    outfilename: str
        name of file to write cohort IDs to
    is_open: bool
        indicates with "save_cohort_results_modal" is open

    Returns:
    --------
    check: bool
        indicates with "save_cohort_results_modal" is open
    write_out_status: str
        indicates if cohort results file has been created

    """
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']:
        raise PreventUpdate

    write_out_status = ""
    if cohort:
        cohort_df = pd.DataFrame.from_dict(cohort)
        cohort_ids = cohort_df['eid'].tolist()
    else:
        cohort_ids = []
        cohort_df = pd.DataFrame()
    if not cohort_ids:
        write_out_status = "No results have been returned, please run a cohort search by navigating to the Configure tab."
        return False, write_out_status
    if outfilename:
        write_out_status = f"Wrote cohort results successfully to {outfilename}"
        try:
            outfile_path = config_init['cohort_path']
            os.path.exists(outfile_path)
        except FileNotFoundError as fe:
            write_out_status = f"outfile path parent directory does not exists, caused following exception {fe}"
        if n2:
            try:
                outfile = os.path.join(outfile_path, outfilename)
                cohort_df.to_csv(outfile, index=False)
                # utils.write_txt_file(outfile, cohort_results)
            except Exception as e:
                write_out_status = f"failed to write cohort ids to file, caused following exception {e}"
    elif not outfilename and n2:
        write_out_status = "No path or filename provided, please provide valid path and filename by clicking the Save cohort IDs button."
    check = toggle_modals(n1, n2, n3, is_open)
    return check, write_out_status

def _create_table(table_dictionary: dict, c: int):
    """Create data_table object from json-encoded table.

    Keyword Arguments:
    ------------------
    table_dictionary: dict
        dictionary containing table contents
    c: int
        counter to assign ID to table object

    Returns:
    --------
    table: html.Div
        html.Div object containing data_table object
    """
    df = pd.DataFrame.from_dict(table_dictionary)
    table = html.Div([dash_table.DataTable(
        id=f'table_{c}',
        columns=[{"name": i, "id": i} for i in df.columns],
        css=[{'selector': '.dash-filter input', 'rule': 'text-align: left'}, {'selector': '.row', 'rule': 'margin: 0'}],
        style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'text-align': 'left'
        },
        data=df.to_dict('records'))])
    return table

def _create_graph(graph_dictionary: dict, c: int):
    """Create Graph object from json-encoded plotly object.

    Keyword Arguments:
    ------------------
    graph_dictionary: dict
        dictionary containing json-encoded plotly object
    c: int
        counter to assign id to graph object

    Returns:
    --------
    table: html.Div
        html.Div object containing Graph object
    """
    fig = plotly.io.from_json(graph_dictionary)
    fig_report = html.Div([dcc.Graph(id=f'graph_{c}', figure=fig)])
    return fig_report


@app.callback(
    [Output("history_results", "children"),
     Output("history_results_report", "children")],
    [Input("cohort_id_results", "modified_timestamp")],
    [State("cohort_id_results", "data"),
     State("cohort_id_report", "data"),
     State("config_store", "data")]
)
def return_results(results_returned: int, results: pd.DataFrame, cohort_id_report: dict, config: dict):
    """Check whether results were returned from cohort search.

    Keyword arguments:
    ------------------
    results_returned: int
        timestamp for when "cohort_id_results" store was last updated
    results: pd.DataFrame
        filtered main dataset for specific cohort
    cohort_id_report: dict
        dict of figures generated by "compute_stats" function in stats module
    config: dict
        contain configuration file paths

    Returns:
    --------
    output_text: dbc object
        indicates whether results were returned by cohort search
    stats_report: dbc object
        dbc object containing list of figures describing cohort

    """
    if results_returned:
        results_df = pd.DataFrame.from_dict(results)
        ids = results_df['eid'].tolist()
        output_text = dbc.Col([html.P(f"Found {len(ids)} matching ids.")])
        stats_report = []
        if cohort_id_report:
            c = 0
            overview = cohort_id_report['tables'].pop(0)
            table = _create_table(overview, c)
            stats_report.append(table)
            for t, g in zip(cohort_id_report['tables'], cohort_id_report['graphs']):
                table = _create_table(t, c)
                fig_report = _create_graph(g, c)
                stats_report.append(fig_report)
                stats_report.append(table)
                c += 1
        final = html.Div(stats_report)
    else:
        output_text = dbc.Col([html.P("No results, please run a cohort search by navigating to the Configure tab.")])
        final = []
    return [output_text], [final]
