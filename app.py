import dash
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from ibapi.contract import Contract
from fintech_ibkr import *
import pandas as pd

# Make a Dash app!
app = dash.Dash(__name__)

# Define the layout.
app.layout = html.Div([

    # Section title
    html.H1("Section 1: Fetch & Display exchange rate historical data"),

    html.H4("Enter a currency pair:"),
    html.P(
        children=[
            "See the various currency pairs here: ",
            html.A(
                "currency pairs",
                href='https://www.interactivebrokers.com/en/index.php?f=2222&exch=ibfxpro&showcategories=FX'
            )
        ]
    ),
    html.Br(),

    # Currency pair text input, within its own div.
    html.Div(
        # The input object itself
        ["Input Currency: ", dcc.Input(
            id='currency-input', value='AUD.CAD', type='text'
        )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block'}
    ),
    # Submit button
    html.Button('Submit', id='submit-button', n_clicks=0),
    # Line break
    html.Br(),
    # Div to hold the initial instructions and the updated info once submit is pressed
    html.Div(id='currency-output', children='Enter a currency code and press submit'),
    html.Br(),


    # endDateTime parameter
    html.H4("Type in the value for endDateTime:"),
    html.Div(
        ["Type in the ending time with format yyyyMMdd HH:mm:ss {TMZ} and press Enter (default is empty and current present moment will be used): ",
         dcc.Input(
             id='end-date-time', value='', type='text', debounce=True
         )]
    ),
    html.Br(),


    # durationStr parameter
    html.H4("Type in the value for durationStr:"),
    html.Div(
        ["Type in the amount of time for which the data needs to be retrieved and press Enter: S (seconds), D (days), W (weeks), M (months), Y (years)",
         dcc.Input(
             id='duration-str', value='30 D', type='text', debounce=True
         )]
    ),
    html.Br(),


    # barSizeSetting parameter
    html.H4("Choose the value for barSizeSetting:"),
    html.Div(
        ["Choose the size of the bar",
         dcc.Dropdown(
             ["1 sec", "5 secs", "15 secs", "30 secs", "1 min", "2 mins", "3 mins",
              "5 mins", '15 mins', "30 mins", "1 hour", "1 day"],
             "1 hour", id='bar-size-setting')]),
    html.Br(),

    # whatToShow parameter
    html.H4("Choose the value for whatToShow:"),
    html.Div(
        ["Choose what kind of information to be retrieved",
         dcc.Dropdown(
             ["TRADES", "MIDPOINT", "BID", "ASK", "BID_ASK", "HISTORICAL_VOLATILITY",
              "OPTION_IMPLIED_VOLATILITY", 'REBATE_RATE', "FEE_RATE", "SCHEDULE"],
             "MIDPOINT", id='what-to-show')]),
    html.Br(),


    # useRTH parameter
    html.H4("Select the value for useRTH:"),
    html.Div(
        ["Select whether to obtain the data generated outside of the Regular Trading Hours (1 for only the RTH data)",
         dcc.RadioItems(
             id='use-rth',
             options=['1', '0'],
             value='1'
         )]),
    html.Br(),

    # Div to hold the candlestick graph
    html.Div([dcc.Graph(id='candlestick-graph')]),
    # Another line break
    html.Br(),
    # Section title
    html.H1("Section 2: Make a Trade"),
    # Div to confirm what trade was made
    html.Div(id='trade-output'),
    # Radio items to select buy or sell
    dcc.RadioItems(
        id='buy-or-sell',
        options=[
            {'label': 'BUY', 'value': 'BUY'},
            {'label': 'SELL', 'value': 'SELL'}
        ],
        value='BUY'
    ),
    # Text input for the currency pair to be traded
    dcc.Input(id='trade-currency', value='AUDCAD', type='text'),
    # Numeric input for the trade amount
    dcc.Input(id='trade-amt', value='20000', type='number'),
    # Submit button for the trade
    html.Button('Trade', id='trade-button', n_clicks=0)
])


# Callback for what to do when submit-button is pressed
@app.callback(
    [  # there's more than one output here, so you have to use square brackets to pass it in as an array.
        Output(component_id='currency-output', component_property='children'),
        Output(component_id='candlestick-graph', component_property='figure')
    ],
    [Input('submit-button', 'n_clicks'), Input('what-to-show', 'value'), Input('bar-size-setting', 'value'),
     Input('use-rth', 'value'), Input('end-date-time', 'value'), Input('duration-str', 'value')],
    # The callback function will fire when the submit button's n_clicks changes
    # The currency input's value is passed in as a "State" because if the user is typing and the value changes, then
    #   the callback function won't run. But the callback does run because the submit button was pressed, then the value
    #   of 'currency-input' at the time the button was pressed DOES get passed in.
    State('currency-input', 'value')
)
def update_candlestick_graph(n_clicks, what_to_show, bar_size_setting, use_rth, end_date_time, duration_str, currency_string):
    # n_clicks doesn't get used, we only include it for the dependency.
    # First things first -- what currency pair history do you want to fetch?
    # Define it as a contract object!
    contract = Contract()
    contract.symbol = currency_string.split(".")[0]  # set this to the FIRST currency (before the ".")
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
    contract.currency = currency_string.split(".")[1]  # set this to the FIRST currency (before the ".")

    ############################################################################
    ############################################################################
    # This block is the one you'll need to work on. UN-comment the code in this
    #   section and alter it to fetch & display your currency data!
    # Make the historical data request.
    # Where indicated below, you need to make a REACTIVE INPUT for each one of
    #   the required inputs for req_historical_data().
    # This resource should help a lot: https://dash.plotly.com/dash-core-components

    # Some default values are provided below to help with your testing.
    # Don't forget -- you'll need to update the signature in this callback
    #   function to include your new vars!
    cph = fetch_historical_data(
        contract=contract,
        endDateTime=end_date_time,
        durationStr=duration_str,
        barSizeSetting=bar_size_setting,
        whatToShow=what_to_show,
        useRTH=use_rth
    )
    # # Make the candlestick figure
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=cph['date'],
                open=cph['open'],
                high=cph['high'],
                low=cph['low'],
                close=cph['close']
            )
        ]
    )
    # # Give the candlestick figure a title
    fig.update_layout(title=('Exchange Rate: ' + currency_string))
    ############################################################################
    ############################################################################

    ############################################################################
    ############################################################################
    # This block returns a candlestick plot of apple stock prices. You'll need
    # to delete or comment out this block and use your currency prices instead.
    # df = pd.read_csv(
    #     'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'
    # )
    # fig = go.Figure(
    #     data=[
    #         go.Candlestick(
    #             x=df['Date'],
    #             open=df['AAPL.Open'],
    #             high=df['AAPL.High'],
    #             low=df['AAPL.Low'],
    #             close=df['AAPL.Close']
    #         )
    #     ]
    # )
    #
    # currency_string = 'default Apple price data fetch'
    ############################################################################
    ############################################################################

    # Return your updated text to currency-output, and the figure to candlestick-graph outputs
    return ('Submitted query for ' + currency_string), fig


# Callback for what to do when trade-button is pressed
@app.callback(
    # We're going to output the result to trade-output
    Output(component_id='trade-output', component_property='children'),
    # We only want to run this callback function when the trade-button is pressed
    Input('trade-button', 'n_clicks'),
    # We DON'T want to run this function whenever buy-or-sell, trade-currency, or trade-amt is updated, so we pass those
    #   in as States, not Inputs:
    [State('buy-or-sell', 'value'), State('trade-currency', 'value'), State('trade-amt', 'value')],
    # We DON'T want to start executing trades just because n_clicks was initialized to 0!!!
    prevent_initial_call=True
)
def trade(n_clicks, action, trade_currency, trade_amt):  # Still don't use n_clicks, but we need the dependency

    # Make the message that we want to send back to trade-output
    msg = action + ' ' + trade_amt + ' ' + trade_currency

    # Make our trade_order object -- a DICTIONARY.
    trade_order = {
        "action": action,
        "trade_currency": trade_currency,
        "trade_amt": trade_amt
    }

    # Return the message, which goes to the trade-output div's "children" attribute.
    return msg


# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)
