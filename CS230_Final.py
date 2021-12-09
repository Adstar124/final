"""
Name: Adam Clarke
CS230: Section 005
Data: Fortune_500_Corporate_Headquarters
Local URL: http://localhost:8501
Public (Published) URL:
Description: This program uses a series of tools learned in CS230 to execute queries related to Fortune 500 companies.
The first query presents companies in multiple states that fall within a user-specified profit range. Data is presented in a pie chart, data table, and map.
The second query will show how many companies in a state fall within a rank range. Data will be presented through a bar graph, data table, and map.
The third query displays all companies within a rank range with a number of employees in a set range. The company locations are shown on a map.
"""

import streamlit as st
import csv
import matplotlib.pyplot as plt
import pandas as pd
import pydeck as pdk


# The title is set with an intro

st.image("500image.jpg",width = 600)
title = '<p style="font-family:Algerian; color:Red; font-size: 50px;">Welcome to the Fortune 500 Streamlit Program!</p>'
st.markdown(title, unsafe_allow_html=True)
st.text("This program was created by Adam Clarke, with assistance from no one, as per the project rules.")

st.sidebar.header("How much do you know about the Fortune 500?")
Q1 = st.sidebar.radio("When did the Fortune 500 Start?", ("No selection","1923", "1884", "1939", "1955"))
if Q1 != "1955":
    st.sidebar.write("Incorrect")
else:
    st.sidebar.write("Correct!")
Q2 = st.sidebar.radio("Who started the Fortune 500?", ("No selection","Adam Smith","Paul Allen Brown","Edgar P. Smith", "Wallace Baker"))
if Q2 != "Edgar P. Smith":
    st.sidebar.write("Incorrect")
else:
    st.sidebar.write("Correct!")
Q3 = st.sidebar.radio("How are companies in the Fortune 500 ranked?",("No selection","By total employees","By annual revenues", "By market cap"))
if Q3 != "By annual revenues":
    st.sidebar.write("Incorrect")
else:
    st.sidebar.write("Correct!")

# The name of the file is made as a variable for the lists/dicts and pandas part
FNAME = "Fortune_500_Corporate_Headquarters.csv"
data = []
def csv_to_dict():  # read to dict

    with open(FNAME, 'r') as csv_file:
        global data
        data = list(csv.DictReader(csv_file))

csv_to_dict()
st.title("Fortune 500 Based on States and Profit")
st.write("Based on your selection of states and a profitability range, a pie chart, table, and map about Fortune 500 companies will be provided.")

# This collects all ofg the states in one list to be selected through the multiselect box
state_list = []
for entry in data:
    if entry["STATE"] not in state_list:
        state_list.append(entry["STATE"])
multi_state_selection = st.multiselect("Please Select Up to Three States", state_list)
st.write(multi_state_selection)

# This grabs the range for the lowest profit so that the sliders for profit range can be created
lowest_profit = 0
for entry in data:
    if float(entry["PROFIT"]) < lowest_profit:
        lowest_profit = float(entry["PROFIT"])
lowest_profit -= 1
highest_profit = 0
for entry in data:
    if float(entry["PROFIT"]) > highest_profit:
        highest_profit = float(entry["PROFIT"])



# These sliders create the profit range
profit_min = st.slider("Choose the lower limit for the profitability range", lowest_profit, highest_profit)
st.write(profit_min)
profit_max = st.slider("Choose the upper limit for the profitability range", lowest_profit + 1, highest_profit + 1)
st.write(profit_max)
if profit_min >= profit_max:
    st.write("The lower limit of the range must be less than the upper limit.")


# This list collects all companies in the selected states within the profit range
profit_state_list = []
for entry in data:
   for state in multi_state_selection:
        if entry["STATE"] == state and float(entry["PROFIT"]) >= profit_min and float(entry["PROFIT"]) <= profit_max:
            profit_state_list.append(entry)

# This just creates a list of each state name
spec_state_list = []
for spec_state in profit_state_list:
    if spec_state not in spec_state_list:
        spec_state_list.append(spec_state["STATE"])

# This creates a dictionary that pairs the state with its frequency within the range
state_full_list = []
state_dict = {}
state_full_list_count = []
for info in profit_state_list:
    state_full_list.append(info["STATE"])
for s in state_full_list:
    if s not in state_dict:
        state_dict[s] = 1
    else:
        state_dict[s] += 1

# This simply creates a list of each state to be used as a label on the below graph
selected_state_list = []
for i in state_dict:
    state_full_list_count.append(state_dict[i])
    selected_state_list.append(i)

# The pie chart is created from the above data
pie, ax = plt.subplots()
ax.pie(state_full_list_count, labels=selected_state_list, autopct='%.1f%%')
plt.title("Fortune 500 Companies Broken Down By State")
st.pyplot(pie)

df_fortune = pd.read_csv(FNAME)

# the dataframe is filtered according to the sliders from above
df_filter_1 = df_fortune.loc[df_fortune["STATE"].isin(selected_state_list)]
df_filter_1 = df_filter_1.loc[df_filter_1["PROFIT"] >=profit_min]
df_filter_1 = df_filter_1.loc[df_filter_1["PROFIT"] <=profit_max]


# The map plots the remaining companies in the dataframe with specific data
def make_map_1(df_filter_1):
    map_filter_1 = df_filter_1.filter(["NAME","RANK","STATE","EMPLOYEES","REVENUES","PROFIT","LATITUDE","LONGITUDE"])
    view_state = pdk.ViewState(latitude=map_filter_1["LATITUDE"].mean(),
                               longitude=map_filter_1["LONGITUDE"].mean(),
                               zoom=3)
    layer = pdk.Layer("ScatterplotLayer",
                      data=map_filter_1,
                      get_position='[LONGITUDE, LATITUDE]',
                      get_radius=18000,
                      get_color = [250,173,100],
                      pickable=True)
    tool_tip = {'html': 'Listing:<br> <b>{NAME}</b>', 'style': {'backgroundColor': 'crimson', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)

    if profit_min > lowest_profit and profit_max>profit_min:
        st.title("Key Company Data")
        st.write(map_filter_1)
        st.title("Company Locations")
        st.pydeck_chart(map)


make_map_1(df_filter_1)

# Line Breaks up each query
# ______________________________________________________________
st.title("Fortune 500 Based on State and Rank")
st.write("Based on you selection of a state and range of ranks in the Fortune 500, a bar graph, table, and map will provide information about companies in the Fortune 500")
# This is a single select to choose a state
single_state_selection = st.selectbox("Please Select a State", state_list)
st.write(single_state_selection)

# The highest lowest ranks
lowest_rank = 501
for entry in data:
    if float(entry["RANK"]) < lowest_rank:
        lowest_rank = float(entry["RANK"])
lowest_rank -= 1
highest_rank = 0
for entry in data:
    if float(entry["RANK"]) > highest_rank:
        highest_rank = float(entry["RANK"])

# These sliders create the rank range
rank_min = st.slider("Choose the lower limit for Fortune 500 Ranks", 1, 500 )
st.write(rank_min)
rank_max = st.slider("Choose the upper limit for Fortune 500 Ranks", 1, 500)
st.write(rank_max)
if rank_min >= rank_max:
    st.write("The lower limit of the range must be less than the upper limit.")

# This creates a list of all companies in a state within the ran range
rank_city_list = []
for entry in data:
    if entry["STATE"] == single_state_selection and int(entry["RANK"]) >= rank_min and int(entry["RANK"]) <= rank_max:
        rank_city_list.append(entry)

# This creates a count section for each city in the state
city_full_list = []
city_dict = {}
city_full_list_count = []
for info in rank_city_list:
    city_full_list.append(info["CITY"])
for s in city_full_list:
    if s not in city_dict:
        city_dict[s] = 1
    else:
        city_dict[s] += 1

# This makes a list of each city in the state
full_city_list = []
for i in city_dict:
    city_full_list_count.append(city_dict[i])
    full_city_list.append(i)
st.write(city_full_list_count)

# This is a graph that represents the results
bar, ax = plt.subplots()
ax.bar(full_city_list, city_full_list_count, color= "g")
plt.title("Fortune 500 Companies By City")
plt.xlabel("Cities")
plt.xticks(rotation=45)
plt.ylabel("Frequency")
st.pyplot(bar)

# the dataframe is filtered according to the sliders from above
df_filter_2 = df_fortune.loc[df_fortune["STATE"] == single_state_selection]
df_filter_2 = df_filter_2.loc[df_filter_2["RANK"] >=rank_min]
df_filter_2 = df_filter_2.loc[df_filter_2["RANK"] <=rank_max]


# The map plots the remaining companies in the dataframe with specific data
def make_map_2(df_filter_2):
    map_filter_2 = df_filter_2.filter(["NAME","RANK","STATE","EMPLOYEES","REVENUES","PROFIT","LATITUDE","LONGITUDE"])
    view_state = pdk.ViewState(latitude=map_filter_2["LATITUDE"].mean(),
                               longitude=map_filter_2["LONGITUDE"].mean(),
                               zoom=3)
    layer = pdk.Layer("ScatterplotLayer",
                      data=map_filter_2,
                      get_position='[LONGITUDE, LATITUDE]',
                      get_radius=18000,
                      get_color = [250,13,180],
                      pickable=True)
    tool_tip = {'html': 'Listing:<br> <b>{NAME}</b>', 'style': {'backgroundColor': 'white', 'color': 'crimson'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)

    if rank_min > lowest_rank and rank_max>rank_min:
        st.title("Key Company Data")
        st.write(map_filter_2)
        st.write("Company Locations")
        st.pydeck_chart(map)


make_map_2(df_filter_2)

# _____________________________________________________________________

st.title("Fortune 500 Based on Employees and Rank")
st.write("The locations and data for all companies that have a user-selected employee count and rank will be shown.")

# This is to find the highest number of employees
highest_employees = 0
for entry in data:
    if int(entry["EMPLOYEES"]) > highest_employees:
        highest_employees = int(entry["EMPLOYEES"])

# These sliders create the employee range
employees_min = st.slider("Choose the lower limit for the number of employees", 0, highest_employees)
st.write(employees_min)
employees_max = st.slider("Choose the upper limit for the number of employees", 0, highest_employees)
st.write(employees_max)
if employees_min >= employees_max:
    st.write("The lower limit of the range must be less than the upper limit.")

highest_rank_2 = int(highest_rank + 1)
# These sliders create the rank range
employees_rank_min = st.slider("Choose the lower limit for Fortune 500 Ranks", 1, highest_rank_2)
st.write(employees_rank_min)
employees_rank_max = st.slider("Choose the upper limit for Fortune 500 Ranks", 1, highest_rank_2)
st.write(employees_rank_max)
if employees_rank_min >= employees_rank_max:
    st.write("The lower limit of the range must be less than the upper limit.")

# the dataframe is filtered according to the sliders from above
df_filter_3 = df_fortune.loc[df_fortune["EMPLOYEES"] >= employees_min]
df_filter_3 = df_filter_3.loc[df_filter_3["EMPLOYEES"] <=employees_max]
df_filter_3 = df_filter_3.loc[df_filter_3["RANK"] >employees_rank_min]
df_filter_3 = df_filter_3.loc[df_filter_3["RANK"] <employees_rank_max]
df_filter_3 = df_filter_3.sort_values(['REVENUES'], ascending=False)



# The map plots the remaining companies in the dataframe with specific data
def make_map_3(df_filter_3):
    map_filter_3 = df_filter_3.filter(["NAME","RANK","STATE","EMPLOYEES","REVENUES","PROFIT","LATITUDE","LONGITUDE"])
    view_state = pdk.ViewState(latitude=map_filter_3["LATITUDE"].mean(),
                               longitude=map_filter_3["LONGITUDE"].mean(),
                               zoom=3)
    layer = pdk.Layer("ScatterplotLayer",
                      data=map_filter_3,
                      get_position='[LONGITUDE, LATITUDE]',
                      get_radius=18000,
                      get_color = [0,180,180],
                      pickable=True)
    tool_tip = {'html': 'Listing:<br> <b>{NAME}</b>', 'style': {'backgroundColor': 'steelblue', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)
    error_val_3 = 0
    if employees_rank_min > lowest_rank and employees_rank_max > employees_rank_min and employees_min > 0 and employees_min < employees_max:
        st.title("Key Company Data")
        st.write(map_filter_3)
        st.title("Company Locations")
        st.pydeck_chart(map)


make_map_3(df_filter_3)

