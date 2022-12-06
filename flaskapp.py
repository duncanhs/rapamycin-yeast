'''

This files describes an interactive website for the visualization of the 
fia tof ms data from Reichling et al 2022. The page contains three tabs 
which deploy the:
    
    trend for the accumulation of metabolites over time for individual mutants
    heatmap of changes compared to wt over time for mutants
    volcano plots with interactive compound identification
    
    
To do: get rid of any data processing in the body and save them as assets that
can be accessed quickly and easily     
    

'''


#%% import your packages

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os as os
import numpy as np
import webbrowser as webbrowser
import json as json
import re as re
import dash_bootstrap_components as dbc
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# declare the server
server = Flask(__name__)

server.wsgi_app = ProxyFix(
    server.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# declare the app

app = Dash(__name__,
           server = server,
           suppress_callback_exceptions = True,
           external_stylesheets = [dbc.themes.FLATLY]
           )

# get some simplified data to play with

dir_path = os.path.dirname(os.path.realpath(__file__))

print(dir_path)

os.chdir(dir_path)

#%% load the data

# load the differential analysis
torfc_ = pd.read_csv("assets/tor_foldchanges.csv", sep = ",").iloc[:,1:]
torpv_ = pd.read_csv("assets/tor_pvalues.csv", sep = ",").iloc[:,1:]
rlpfc_ = pd.read_csv("assets/rlp_foldchanges.csv", sep = ",").iloc[:,1:]
rlppv_ = pd.read_csv("assets/rlp_pvalues.csv", sep = ",").iloc[:,1:]

# load the ion information
ions_ = pd.read_csv("assets/ions.csv", sep = ",").iloc[:,1:]

# load the averages and standard deviations

torav_ = pd.read_csv("assets/tor_averages.csv", sep = ",")
torsd_ = pd.read_csv("assets/tor_stdev.csv", sep = ",")

rlpav_ = pd.read_csv("assets/rlp_averages.csv", sep = ",")
rlpsd_ = pd.read_csv("assets/rlp_stdev.csv", sep = ",")

# get the addresses for the kegg ids

ions_keggid_ = ions_.Top_annotation_ids

ions_name_ = ions_.Top_annotation_name

firstkegg_ = [x.split(";")[0] for x in ions_keggid_]

urls_ = [("https://www.genome.jp/entry/" + x) for x in firstkegg_]

# so you are going to want to have lists of genes, times, and you will want
# to be able to tell which of the datasets are being selected when you
# choose a particular drug in a dropdown

# get the pertubations
torperts_ = torav_.columns.tolist()

rlpperts_ = rlpav_.columns.tolist()

# split it

torsplit_ = [x.split("_") for x in torperts_]

rlpsplit_ = [x.split("_") for x in rlpperts_]

# get the times and the genes

torgenes_ = [x[0] for x in torsplit_]

rlpgenes_ = [x[0] for x in rlpsplit_]

tortimes_ =  [float(x[1]) for x in torsplit_]

rlptimes_ =  [float(x[1]) for x in rlpsplit_]

# now you can combine the genes (except wt) to make the dropdown list

combinedgenes_ = torgenes_.copy()

combinedgenes_.extend(rlpgenes_)

combinedgenesu_ = pd.Series(combinedgenes_).unique()

combinedgenesu_ = combinedgenesu_[combinedgenesu_ != "WT"]

# also make a combined dataframe for easier plotting in heatmap and 
# volcano plots

allfcs_ = pd.concat((torfc_, rlpfc_), axis =1)

allpvs_ = pd.concat((torpv_, rlppv_), axis =1)

# get the fc gene names and fold changes

fcsplit_ =  [x.split("_") for x in allfcs_.columns]

fcgenes_ = [x[0] for x in fcsplit_]

fctimes_ = [float(x[1]) for x in fcsplit_]

# also get the unique gene names from here to save trouble later

fcgenesu_ = pd.Series(fcgenes_).unique()

# so, in order to make sure you can get your plots with one 
# dropdown, it's important to make sure that the combinedgenesu_ that are not 
# in the fc data are discarded as options

selgoodgenes_ = [x in fcgenesu_ for x in combinedgenesu_]

combinedgenesu_ = combinedgenesu_ [selgoodgenes_]

#%% set the shaded line plot layout

lineplot_layout_ = html.Div([
    
    html.Div([
        
        html.H4('Metabolite intensities versus time after rapamycin treatment'),
        html.P('Slect your desired mutant and metabolite to see the effect'
               'of rapamycin treatment on its accumulation versus time')       
        ],
        className = 'h-80 p-5 text-white bg-secondary rounded-3', style = {
            'margin-bottom': '2rem'}),
    
    dbc.Row(
        dbc.Col([
            
            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        id='metabolite_line_',
                        options= ions_name_,
                        value= "Phenylalanine",
                        multi = False,
                        style = {"font-size": "100%"}),
                    width = 6),
                style = {"margin-bottom": "2rem"},
                justify = 'center'
                ),
            
                dcc.Graph(id="line_graph"),
                dbc.Row(
        
       
            html.P('The average intensities for the indicated metabolite'
                   ' are represented by the central line for WT and the'
                   ' chosen mutant. The shaded area indicates the standard'
                   ' deviation for the average at that time point and'
                   ' mutant.')
        )], width = 6),
        justify = 'center',
        style = {"height": "150%",
                 #'margin-left': '15%'
                 }),
    
    
    
    ])


#%% set the heatmap layout
heatmap_layout_ = html.Div([


    html.Div([
        
        html.H4("Metabolite fold-change heatmap"),
        html.P("Select your desired mutant and filter metabolites "
               "based on p-value or fold-change magnitude")],
        className = "h-80 p-5 text-white bg-secondary rounded-3", style = {
            'margin-bottom': '2rem'}),
    
    
    
    dbc.Row([
        dbc.Col([
            dbc.Row([dbc.Button("Download mutant names",
                               color = "primary",
                               id = "mutant_button_",
                               className = "mb-3"),
                     dcc.Download(id="mutants_csv_")]),          
            dbc.Row(html.P("Log2 fold change cutoff")),
            dbc.Row(dcc.Input(id = "fc_cutoff",
                          value = 0.75,
                          type = "number"), style = {"margin-left": "2px",
                                                     "margin-bottom": "2rem"}),
            dbc.Row(html.P("p-value cutoff")),
            dbc.Row(dcc.Input(id = "pv_cutoff",
                              value = 0.05,
                              type = "number"), style = {"margin-left": "2px",
                                                         "margin-bottom": "2rem"})
            ], width = 2),
        
        dbc.Col([dbc.Row(dcc.Graph(id="graph")),
                 dbc.Row(html.P(
                     "The average log2 transformed fold-changes for the indicated"
                    " mutant compared to WT is displayed after 0 through 90 minutes"
                    " of treatment with rapamycin. Fold change and p-value cut-"
                    "offs can be chosen to include metabolites as desiered for "
                    "your purposes."
                    ))],
                 width = 8)
            
        ], style = {"height": "150%"},
           justify = 'center'),
    ])
   

#%% set the volano plot layout

volcano_layout_ =  html.Div([
    
    html.Div([
        html.H2('Volcano plot'),
        html.P("Select your desired drug and choose significance thresholds "
               "based on p-value or fold-change magnitude"),
        #html.P("You may also select a point by clicking "
        #       "for additional compound information")
        ],
        className = "h-80 p-5 text-white bg-secondary rounded-3", style = {
            'margin-bottom': '2rem'}),
    
    dbc.Row([
        
        
        dbc.Col([
            
            html.Div([
                html.P("Time point:"),
                dcc.Dropdown(id = "timesel_",
                             
                             options = (0, 5, 30, 60, 90),
                             value = 60,
                             style = {'margin-bottom': '2rem'}),
                ]),

            html.Div([
                html.P("Log2 fold change cutoff"),
                dcc.Input(id = "fc_cutoff2",
                          value = 0.75,
                          type = "number"
                , style = {'margin-bottom': '2rem'}),
                ]),
            html.Div([
                html.P("p-value cutoff",
                    style = {"font-family": "Arial" }),
                dcc.Input(id = "pv_cutoff2",
                          value = 0.01,
                          type = "number"
                , style = {'margin-bottom': '2rem'}),
                html.Div(id = "click-output")
            ]),
            #html.P("Click on a point to see metabolite information")
            
            
            ], width = 2),
        
        dbc.Col([dbc.Row(
            dcc.Graph(id="graph2")),
            dbc.Row(
                html.P('The average log2 transformed fold-change for the' 
                       ' selected time and mutant compared to WT are shown '
                       'for each metabolite measured. Selections can be made '
                       'for significance cutoffs in terms of the magnitude of'
                       ' the change or p-value. Metabolite information can be'
                       ' retrieved from KEGG by clicking on a metabolite on'
                       ' the graph.'))
            ], width = 7,
            style = {'margin-left': '1rem'})
        ],
        justify = 'center'
        )
    ])


#%% main app layout

subtext1_ = html.P(
    dcc.Markdown("This is an interactive data viewer for "
                                  
                 '''[Reichling *et al.* 2022.](https://www.biorxiv.org/content/10.1101/2022.07.25.500770v1)'''
                 
                 " Please cite use if you use this data in your own publication"
    )
)
    
    
subtext2_ = html.P(
    dcc.Markdown(
        '''
        #### Abstract
        
        Although the genetic code of the yeast Saccharomyces cerevisiae was sequenced 25 years ago,
        the characterization of the roles of genes within it is far from complete. The lack of a 
        complete mapping of functions to genes hampers systematic understanding of the biology of the 
        cell. The advent of high-throughput metabolomics offers a unique approach to uncovering gene 
        function with an attractive combination of cost, robustness, and breadth of applicability. 
        Here we used flow-injection time-of-flight mass spectrometry (FIA-MS) to dynamically profile 
        the metabolome of 164 loss-of-function mutants in TOR and receptor or receptor-like genes under 
        a time-course of rapamycin treatment, generating a dataset with over 7,000 metabolomics 
        measurements. We demonstrate that dynamic metabolite responses to rapamycin are more 
        informative than steady state responses when recovering known regulators of TOR signaling,
        as well as identifying new ones. Deletion of a subset of the novel genes causes phenotypes 
        and proteome responses to rapamycin that further implicate them in TOR signaling. We found 
        that one of these genes, CFF1, was connected to the regulation of pyrimidine biosynthesis 
        through URA10. These results demonstrate the efficacy of the approach for flagging novel 
        potential TOR signaling-related genes and highlights the utility of dynamic perturbations 
        when using functional metabolomics to deliver biological insight.
        
        
        Below you will find interactive plotting tools that make it possible to explore the main
        metabolomics dataset within the study. 
        
        '''
        )
    
    )

app.layout = html.Div([
    
        html.Div([
            
            html.Div(
                [html.H2(
                    
                    dcc.Markdown("The metabolome response of *S. cerevisiae*"
                                 " loss-of-function mutants to rapamycin"),
                         className="display-3"),
                 html.Hr(className="my-2"),
                 
                 subtext1_,
                 subtext2_
                 
                 ], 
                className="h-80 p-5 text-white rounded-3",
                style = {"background-image": 'url("./assets/waves.jpg")',
                         "verticalAlign": "middle",
                         "background-size": 'contain',
                         'margin-bottom': '2rem',
                         }
                ),
            
            dbc.Row([
                
                dbc.Col(
                    html.H4("Mutant:"),
                    width = 1),
                
                dbc.Col(
                    dcc.Dropdown(
                    id='gene_selector_',
                    options= combinedgenesu_,
                    value= "GTR1",
                    multi = False,
                    style = {"font-size": "100%"}),
                    width = 2
                    )],
                style = {"margin-bottom": "2rem"}),
            
            dbc.Tabs([
                dbc.Tab(label = 'Line plots', tab_id = 'lineplots'),
                dbc.Tab(label = 'Heatmapping', tab_id = 'heatmaps'),
                dbc.Tab(label = 'Volcano plots', tab_id = 'volcanoplot')
                ],
                id = 'tabs_',
                active_tab = 'lineplots',
                style = {
                    'font-size': '25px',
                    "borderWidth": "1px"
                    
                    }),
            
            html.Div(
                id = 'tab_content'
                ),
            html.P(
                
                dcc.Markdown(
                    
                    "__This work is licensed under:__ "
                    '''[Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
                    ''',
                    
                    style = {'font-size': '12px',
                             'margin-top': '4rem'}
                    
                    )
                
                )
            ])
        ], style = {'margin-left': '2rem',
                 'margin-top': '2rem',
                 'margin-right': '2rem'})


#%%  set up the tab system 

@app.callback(
    Output("tab_content", "children"),
    Input("tabs_", "active_tab")
    )
     
def render_tab_content(active_tab_):
    
    if active_tab_ == 'lineplots':
        
        return lineplot_layout_
    
    if active_tab_ == "heatmaps":
        
        return heatmap_layout_
    
    if active_tab_ == 'volcanoplot':
        
        return volcano_layout_
    
   
               
#%% area line plot callback and plotting



# definte the callbacks
@app.callback(

    Output("line_graph", "figure"),
    Input('gene_selector_', 'value'),
    Input("metabolite_line_", "value")
    )                    

# define the figure plotting function

def area_line_(choose_gene_, choose_met_):
    
    # first determine if the gene is from the rlp or tor dataset
    # and choose your data subset accordingly
    
    if choose_gene_ in torgenes_:
        
        currentgenes_ = torgenes_

        currentavs_ = torav_
        
        currentsds_ = torsd_
        
    else:
        
        currentgenes_ = rlpgenes_
        
        currentavs_ = rlpav_
        
        currentsds_ = rlpsd_        
        
    
    # subset the current date with the gene you want and the wt

    mutav_ = currentavs_.loc[choose_met_ == ions_name_,
                               [x == choose_gene_ for x in currentgenes_]]

    wtav_ =   currentavs_.loc[choose_met_ == ions_name_,
                               [x == "WT" for x in currentgenes_]]
    
    mutsd_ = currentsds_.loc[choose_met_ == ions_name_,
                               [x == choose_gene_ for x in currentgenes_]]

    wtsd_ =   currentsds_.loc[choose_met_ == ions_name_,
                               [x == "WT" for x in currentgenes_]]
    
    # now you want to construct two different dataframes with all the
    # required data
    
    # first for the wt
    
    wtdata_ = pd.concat((pd.DataFrame(wtav_).transpose(),
                           pd.DataFrame(wtsd_).transpose()), axis = 1)
    
    wtdata_.columns = ['avg', 'std']
    
    wtdata_['upper'] = wtdata_['avg'] + wtdata_['std']
    
    wtdata_['lower'] = wtdata_['avg'] - wtdata_['std']
    
    # get the current genes and times
    
    indexsplit_ = [x.split("_") for x in wtdata_.index]
    
    wtdata_['gene'] = [x[0] for x in indexsplit_]
    
    wtdata_['time'] = [float(x[1]) for x in indexsplit_]
        
    wtdata_ = wtdata_.sort_values('time')
 
    # now that you have everything put together how you would like it
    # i think you want to reset the index
    
    wtdata_ = wtdata_.reset_index(drop = True)

    # then with the mutant
    
    mutdata_ = pd.concat((pd.DataFrame(mutav_).transpose(),
                           pd.DataFrame(mutsd_).transpose()), axis = 1)
    
    mutdata_.columns = ['avg', 'std']
    
    mutdata_['upper'] = mutdata_['avg'] + mutdata_['std']
    
    mutdata_['lower'] = mutdata_['avg'] - mutdata_['std']
    
    # get the current genes and times
    
    indexsplit_ = [x.split("_") for x in mutdata_.index]
    
    mutdata_['gene'] = [x[0] for x in indexsplit_]
    
    mutdata_['time'] = [float(x[1]) for x in indexsplit_]
        
    mutdata_ = mutdata_.sort_values('time')
 
    # now that you have everything put together how you would like it
    # i think you want to reset the index
    
    mutdata_ = mutdata_.reset_index(drop = True)
    
    # you will have to order the times from smallest to largest to make it
    # plot things correctly

    
    # define your colours
    
    steelblue_ = 'rgba(70,130,180,0.5)'
    steelbluet_ = 'rgba(70,130,180,0.2)'
    
    darkorange_ = 'rgba(255,140,0,0.5)'
    darkoranget_= 'rgba(255,140,0,0.2)'
    
    # finally you can make the plot
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        
        #x = wtdata_['time'] + wtdata_['time_r'],
        x = wtdata_['time'],
        #y = wtdata_['upper'], wtdata_['lower'],
        y = wtdata_['upper'],
        #line_color = 'white',
        line = dict(width = 0),
        showlegend= False
                
        ))
        
    fig.add_trace(go.Scatter(
        
        #x = wtdata_['time'] + wtdata_['time_r'],
        x = wtdata_['time'],
        #y = wtdata_['upper'], wtdata_['lower'],
        y = wtdata_['lower'],
        fill = 'tonexty',
        fillcolor = darkoranget_,
        #line_color = 'none',
        line = dict(width = 0),
        showlegend= False
        ))
    
        
    
    fig.add_trace(go.Scatter(
        
        x = wtdata_['time'],
        y = wtdata_['avg'],
        line_color = darkorange_,
        name = "WT"
        ))
    
    # do the same for the mutant
    
    fig.add_trace(go.Scatter(
        
        #x = mutdata_['time'] + mutdata_['time_r'],
        x = mutdata_['time'],
        #y = mutdata_['upper'], mutdata_['lower'],
        y = mutdata_['upper'],
        #line_color = 'white',
        line = dict(width = 0),
        showlegend= False
                
        ))
        
    fig.add_trace(go.Scatter(
        
        #x = mutdata_['time'] + mutdata_['time_r'],
        x = mutdata_['time'],
        #y = mutdata_['upper'], mutdata_['lower'],
        y = mutdata_['lower'],
        fill = 'tonexty',
        fillcolor = steelbluet_,
        #line_color = 'none',
        line = dict(width = 0),
        showlegend= False
        ))
    
    
    last_x = mutdata_['time']
    
    last_y = mutdata_['avg']
    
    fig.add_trace(go.Scatter(
        
        x = last_x,
        y = last_y,
        line_color = steelblue_,
        name = choose_gene_
        ))
    
    
    fig.update_traces(mode = 'lines')
    
    fig.update_layout(template = 'simple_white',
                      xaxis_title = 'Time (minutes)',
                      yaxis_title = 'Intensity (A.U.)')
    
    
    #plot(fig)
    
    return fig

  
    
    

                    
                    
#%% heatmap callback and plotting
# define callbacks


@app.callback(
    #Output("Drug_names", "value"),
    Output("graph", "figure"),
    Input('gene_selector_', 'value'),
    Input("fc_cutoff", "value"),
    Input("pv_cutoff", "value"))

# define the plotting function

def filter_heatmap(mut_, fccut_, pvcut_):
    
    # first you need to find the mutant that you are working with
    
    selmut_ = mut_ == pd.Series(fcgenes_)
    
    df_ = allfcs_[allfcs_.columns[selmut_]]
    
    pvdf_ = allpvs_[allpvs_.columns[selmut_]]
    
    times_ = pd.Series(fctimes_)[selmut_]
        
    currentdata_ = df_.copy().transpose()
    
    currentpvs_ = pvdf_.copy().transpose()

    # add the ion names as the column names
    
    currentdata_.columns = ions_name_
    
    currentpvs_.columns = ions_name_
        
        
    # get the maximum absolute log2fc for each row
    
    maxabs_ = currentdata_.apply(lambda x: max(abs(x)), 0)
    
    minpvs_ = currentpvs_.apply(min, 0)
    
    # filter out small rows
     
    fcsel_ = maxabs_ > fccut_
    
    pvsel_ = minpvs_ < pvcut_
               
    filtereddata_ = currentdata_[currentdata_.columns[fcsel_ & pvsel_]]
    
    
    # make the column names much shorter
    
    currentcolnames_ = pd.Series(filtereddata_.columns)

    shortcolnames_ = currentcolnames_.copy()
    
    for i_ in range(len(shortcolnames_)):
        
        if len(shortcolnames_[i_]) > 15:
            
            shortcolnames_[i_] = shortcolnames_[i_][:15] + "..."
            
    filtereddata_.columns = shortcolnames_


    # reorder the rows according to the values of the time
    
    np.argsort(times_)
    
    filtereddata_ = filtereddata_.loc[filtereddata_.index[np.argsort(times_)]]

    # now it would be nice to cluster the columns

        
    
    fig = px.imshow(filtereddata_,
                    color_continuous_scale= "RdBu_r",
                    aspect = "auto",
                    color_continuous_midpoint = 0,
                    template = "simple_white",
                    labels = dict(x = "Metabolites",
                                  y = "Mutant and time (min)"))
    
    #px.update_layout(xaxis_title = "Metabolites",
    #                 yaxis_title = "Mutant name and treatment time (minutes)")
    #plot(fig)
    
    return fig

#%% volcano plot callback and plotting

@app.callback(
Output("graph2", "figure"),
Input('gene_selector_', 'value'),
Input("timesel_", "value"),
Input("fc_cutoff2", "value"),
Input("pv_cutoff2", "value"))

def volcano_plot(mutantchoose2_, timechoose_, fccut_, pvcut_):
    
    # make a selector for time
    
    fctimesel_ = timechoose_ == pd.Series(fctimes_)
    
    # make a selector for the gene
    
    fcgenessel_ = mutantchoose2_ == pd.Series(fcgenes_)
    
    # make a combined selection
    
    combsel_ = fctimesel_ & fcgenessel_ 
    
    # get the data you are going to plot
    
    volcano_fc_ = allfcs_[allfcs_.columns[combsel_]].copy()
    
    volcano_pv_ = allpvs_[allpvs_.columns[combsel_]].copy()
    
    ionnames_ = ions_.Top_annotation_name
    
    # get a colour to label the significant ions with
    
    fcsel_ = abs(volcano_fc_) > fccut_
    
    pvsel_ = volcano_pv_ < pvcut_
    
    combsel_ = (fcsel_ & pvsel_).iloc[:,0]

    sig_ = pd.Series(["not significant"] * len(volcano_fc_.index))
    
    sig_[combsel_] = "significant"    
    
    sigser_ = pd.Series(sig_)
    
    # now use the cutoffs to figure out the colouring of the 
    # points on the volcano plot
    
    volcano_df_ = pd.concat([volcano_fc_, -np.log10(volcano_pv_), sigser_, pd.Series(urls_)],
                            axis = 1)
    
    volcano_df_.columns = ["fcs", "pvs", "sig", "u"]
    
    volcano_df_.index = ionnames_
        
    
    # plot the figure
    
    fig = px.scatter(volcano_df_,
                     x = "fcs",
                     y = "pvs",
                     hover_name = ionnames_,
                     template = "simple_white",
                     color = "sig",
                     custom_data= "u")
    
    fig.update_layout(xaxis_title = "Log2(Fold-change)",
                      yaxis_title = "-Log10(p-value)",
                      legend_title = "")
    
    #plot(fig)
       
    return fig

@app.callback(
    Output('click-output', 'value'),
    Input('graph2', 'clickData')
       
)


def openurl(clickData):
    
    if clickData != None:
        
        jsontext_ = json.dumps(clickData, indent = 2)
        
        left_ = jsontext_.split( "ata\": [")[1]
        
        currenturl_ = left_.split("]")[0]
        
        currenturl_ = re.sub(" ", "", currenturl_)
        currenturl_ = re.sub("/t", "", currenturl_)
        currenturl_ = re.sub("\"", "", currenturl_)
        
        #set the path for chrome
        chrome_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        webbrowser.register('chrome', None,webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get("chrome").open(currenturl_, 2)
        
        webbrowser.open_new_tab(currenturl_)
    
        #return currenturl_

#%% download drug names


@app.callback(
    Output("mutants_csv_", "data"),
    Input("mutant_button_", "n_clicks"),
    prevent_initial_call=True    
    )

# allow the user to download the drug names

def func(n_clicks):
    
    drug_dataframe = pd.DataFrame(fcgenesu_)
    
    drug_dataframe.columns = ["mutant_names"]
    
    return dcc.send_data_frame(drug_dataframe.to_csv, "mutant_names.csv", index = False)

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
#@app.route('/')

#app.run_server(debug=True)

if __name__ == '__main__':
    app.run_server(
    #app.run(
        host='0.0.0.0',
        port=8080
         )
    #app.run_server(host = '0.0.0.0', debug=True)
    #serve(server, host='0.0.0.0', port=5000, url_scheme = 'https')