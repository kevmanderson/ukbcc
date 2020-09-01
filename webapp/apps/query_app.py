import dash
from app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import pandas as pd
import os

from ukbcc import query, utils
import pprint

from datetime import datetime
print_time = lambda: datetime.now().strftime("%H:%M:%S")

from dash.exceptions import PreventUpdate

all_dropdown = dbc.FormGroup(
    [
        dbc.Label("All of these", html_for="example-email"),
        dcc.Dropdown(id={"index":0, "name":"query_term_dropdown"}, placeholder="Enter defined terms", clearable=True, multi=True, persistence=False),
        dbc.FormText(
            "Add terms that must all be present for an individual to be included in the cohort",
            color="secondary",
        ),
    ]
)

any_dropdown = dbc.FormGroup(
    [
        dbc.Label("Any of these", html_for="example-email"),
        dcc.Dropdown(id={"index":1, "name":"query_term_dropdown"}, placeholder="Enter defined terms", clearable=True, multi=True, persistence=False),
        dbc.FormText(
            "Add terms that are optionally present for an individual to be included in the cohort",
            color="secondary",
        ),
    ]
)


none_dropdown = dbc.FormGroup(
    [
        dbc.Label("None of these", html_for="example-email"),
        dcc.Dropdown(id={"index":2, "name":"query_term_dropdown"}, placeholder="Enter defined terms", clearable=True, multi=True, persistence=False),
        dbc.FormText(
            "Add terms that must be absent for an individual to be included in the cohort",
            color="secondary",
        ),
    ]
)


#
#
# Keyword Search Tab
#
tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Cohort Search", className="card-text"),
            html.P("Define the properties of a cohort, based on the defined terms and show results", className="card-text"),
            dbc.Form(
                dbc.FormGroup([all_dropdown, any_dropdown, none_dropdown,
                               dbc.Button("Submit", color="success", id='cohort_search_submit1', style={"margin": "5px"})])
            ),
            dbc.Row(dbc.Col(id='query_results'), align='center'),
            dbc.Row([
               dbc.Button("Previous", color='primary', id={"name":"prev_button_query","type":"nav_btn"}, style={"margin": "5px"}),
               dbc.Button("Next", color='primary',  id={"name":"next_button_query","type":"nav_btn"}, style={"margin": "5px"})
            ]),

            dbc.Modal(
                [
                    dbc.ModalHeader("Running query..."),
                    dbc.ModalBody(id="run_query", children="Please wait, this could take some time.."),
                    # dbc.Row(dbc.Col(id="status_message"))),
                    # dbc.Row(dbc.Col(id="query_output"))),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close_run_query_btn", className="ml-auto", style={"margin": "5px"})
                    ),
                ],
                id="run_query_modal")
        ]
    ),
    className="mt-3",
)

# @app.callback(
#     Output("run_query", "children"),
#     [Input("cohort_search_submit1", "n_clicks")]
# )
# def update_run_query_modal(n_click):
#     return dbc.Row(
#                 dbc.Col([
#                     html.P("Please wait, this could take some time...")
#                 ]))

def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("run_query_modal", "is_open"),
    [Input("cohort_search_submit1", "n_clicks"),
    Input("close_run_query_btn", "n_clicks")],
    [State("run_query_modal", "is_open")]
)
def toggle_run_query_modal(n1, n2, is_open):
    check = toggle_modal(n1, n2, is_open)
    return check
#
# When we load the derived terms update, so does the list of searchable terms
#
@app.callback(
    Output({"index":MATCH, "name":"query_term_dropdown"}, 'options'),
    [Input({"index":MATCH, "name":"query_term_dropdown"}, 'value')],
    [State('defined_terms', 'data')]
)
def set_querable_terms(active_tab, defined_terms):
    # If we have no defined terms, sop this callback
    if (defined_terms is None):
        print(defined_terms)
        raise PreventUpdate

    opts=[ {'label': val['name'][0], 'value': key} for key,val in defined_terms.items()]
    return(opts)


def _term_iterator(id: str, defined_terms: dict):
    """Creates list of tuples from defined_terms dictionary.

    Iterates through field, value combinations within defined_terms[id]['any']
    and appends them to a list as tuples of (key, value)

    Keyword arguments:
    ------------------
    id: str
        id to use as key for defined_terms dict
    defined_terms: dict
        dictionary returned by alter_defined_term function in "definitions_app.py"

    Returns:
    --------
    rand_terms: list
        list of tuples of encoded field, value combinations
    decoded_terms: list
        list of tuples of decoded field, value combinations

    """
    rand_terms = []
    rand_terms_decoded = []
    terms = pd.concat([pd.read_json(x) for x in defined_terms[id]['any']] + [pd.DataFrame()])
    terms['FieldID'] = terms['FieldID'].astype(str)
    terms['Value'] = terms['Value'].astype(str)
    rand_terms = rand_terms + [tuple(x) for x in terms[['FieldID', 'Value']].values]
    rand_terms_decoded = rand_terms_decoded + [tuple(x) for x in terms[['Field', 'Meaning']].values]
    return rand_terms, rand_terms_decoded

# switch to history/results tab
# @app.callback(Output('tabs', 'active_tab'),
#           [Input('query_results', 'modified_timestamp')])
# def switch_tab(results, *params):
#     print("inside switch tabs")
#     if results:
#         print("clicks {}".format(clicks))
#         return history_app.tab
#
# Submit a query
#
@app.callback(
    [Output("query_results", "children"),
    Output("cohort_id_results", "data")],
    [Input("cohort_search_submit1", "n_clicks")],
    [State("defined_terms", "data"),
     State({"index":0, "name":"query_term_dropdown"}, 'value'),
     State({"index":1, "name":"query_term_dropdown"}, 'value'),
     State({"index":2, "name":"query_term_dropdown"}, 'value'),
     State("config_store", "data")]
)
def submit_cohort_query(n, defined_terms, all_terms, any_terms, none_terms, config):
    print('\nsubmit_cohort_query()')
    pp = pprint.PrettyPrinter(indent=4)

    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    if n is None:
        raise PreventUpdate

    #Put data in the right for for the ukbcc backend
    anys = []
    nones = []
    alls = []
    anys_decoded = []
    nones_decoded = []
    alls_decoded = []

    print("defined terms {}".format(defined_terms))

    if all_terms:
        for id in all_terms:
            alls, alls_decoded = _term_iterator(id, defined_terms)

    if any_terms:
        for id in any_terms:
            anys, anys_decoded = _term_iterator(id, defined_terms)

    if none_terms:
        for id in none_terms:
            nones, nones_decoded = _term_iterator(id, defined_terms)

    print("any terms {}, all terms {}, none terms {}".format(anys, alls, nones))

    cohort_dictionaries = {"encoded": {"all_of": alls, "any_of": anys, "none_of": nones},
                           "decoded": {"all_of": alls_decoded, "any_of": anys_decoded, "none_of": nones_decoded}}

    outpath = config['cohort_path']

    for k, v in cohort_dictionaries.items():
        print("cohort {} {}".format(k, v))
        name = "cohort_dictionary_" + k + ".txt"
        cohort_out = os.path.join(outpath, name)
        utils.write_dictionary(v, cohort_out)
        if os.path.exists(cohort_out):
            print(f"successfully saved {k} cohort dictionary to {cohort_out}")
        else:
            print(f"could not save {k} cohort dictionary to {cohort_out}")


    # cohort_out_decoded = os.path.join(outpath, "cohort_dictionary_decoded.txt")
    # cohort_out_encoded = os.path.join(outpath, "cohort_dictionary_encoded.txt")
    #
    # utils.write_dictionary(cohort_criteria_decoded, cohort_out_decoded)
    # utils.write_dictionary(cohort_criteria_encoded, cohort_out_encoded)

    # if os.path.exists(cohort_out_decoded):
    #     print(f"successfully saved decoded cohort dictionary to {cohort_out_decoded}")
    # else:
    #     print(f"could not save cohort dictionary to {cohort_out_decoded}")
    #
    # if os.path.exists(cohort_out_encoded):
    #     print(f"successfully saved encoded cohort dictionary to {cohort_out_encoded}")
    # else:
    #     print(f"could not save cohort dictionary to {cohort_out_encoded}")

    print('\ncreate_queries {}'.format(print_time()))
    queries = query.create_queries(cohort_criteria=cohort_dictionaries['encoded'], main_filename=config['main_path'],
                                   gpc_path=config['gp_path'])
    pp.pprint(queries)
    print('\nquery_databases {}'.format(print_time()))
    ids = query.query_databases(cohort_criteria=cohort_dictionaries['encoded'], queries=queries, main_filename=config['main_path'],
                          write_dir=config['cohort_path'], gpc_path=config['gp_path'], out_filename=config['out_filename'], write=False)
    print(ids)
    print('\nfinished query_databases {}'.format(print_time()))

     # output_form = dbc.FormGroup([
     #        dbc.Label("Name of file to write IDs to", html_for={"type": "config", "name":"codings_path"}),
     #        dbc.Input(placeholder="Specify the directory to save the output files to e.g /data/ukbcc_output.", type="text", id={"type": "config", "name": "cohort_path"},
     #        persistence=True),
     #        dbc.FormText("Directory path to save output files to", color="secondary")])
    footer = dbc.ModalFooter(dbc.Button("Close", id="close_run_query_btn_new", className="ml-auto", style={"margin": "5px"}))
    output_text = html.P(f"Found {len(ids)} matching ids.")
    output_runquery = dbc.Row(dbc.Col([output_text,
                                       dbc.Button("Close", color='primary', id="run_query_close", style={"margin": "5px"})]))
     # output_queryresults = dbc.Row(dbc.Col([]))
    return output_text, ids
