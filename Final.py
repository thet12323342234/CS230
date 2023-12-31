"""
Class: CS230--Section 3
Name: Leo Susi
Description: Below I have completed my final project using Streamlit, data analytics, and previously covered materials.
I used resources from https://bluebikes.com/system-data to better understand the data that I was manipulating throughout the project
I pledge that I have completed the programming assignment
independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""

import streamlit as st                                                                              # Import the Streamlit library for creating the web app
import pandas as pd                                                                                 # Import the Pandas library for data manipulation
import matplotlib.pyplot as plt                                                                     # Import Matplotlib for data visualization
from PIL import Image


@st.cache_data                                                                                      # Decorator to cache the result of this function
def load_data():                                                                                    # Function to load data
    bluebike_stations = pd.read_csv('current_bluebike_stations.csv')
    tripdata = pd.read_csv('hubway-tripdata.csv')
    return bluebike_stations, tripdata                                                              # Return loaded data


def get_top_bikes(tripdata, top_n=10):                                                              # Function to get top bike usage data
    return tripdata['bikeid'].value_counts().head(top_n)


def plot_top_bikes(top_bikes):                                                                      # Function to plot bar chart for top bikes
    plt.figure(figsize=(10, 6))                                                                     # Create a bar chart to display top bike usage
    top_bikes.plot(kind='bar', color='blue')
    plt.title('Top 10 Most Frequently Used Bikes by ID')
    plt.xlabel('Bike ID')
    plt.ylabel('Usage Count')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    return plt


def get_user_type_count(tripdata):                                                                  # Function to get user type count (subscribers vs customers)
    return pd.DataFrame(tripdata['usertype'].value_counts()).rename(columns={'usertype': 'count'})


def plot_user_type_count(user_type_count, show_subscribers=True,
                         show_customers=True):                                                      # Updated function to plot user type count (subscribers vs customers)
    plt.figure(figsize=(8, 5))                                                                      # Create a bar chart to display user type count

    if show_subscribers and show_customers:                                                         # Check and plot based on user selection
        bars = plt.bar(user_type_count.index, user_type_count['count'],
                       color=[('blue' if x == 'Subscriber' else 'green') for x in user_type_count.index])
    elif show_subscribers:
        bars = plt.bar('Subscriber', user_type_count.loc['Subscriber', 'count'], color='blue')
    elif show_customers:
        bars = plt.bar('Customer', user_type_count.loc['Customer', 'count'], color='green')

    plt.title('Total Number of Trips by User Type')
    plt.xlabel('User Type')
    plt.ylabel('Number of Trips')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    return plt


def get_station_usage(tripdata, top_n=3):                                                           # Function to calculate top start and stop station usage
    top_start_stations = tripdata['start station id'].value_counts().head(top_n)
    top_stop_stations = tripdata['end station id'].value_counts().head(top_n)
    return top_start_stations, top_stop_stations


def get_station_usage_by_name(tripdata, top_n=3):                                                   # Function to calculate top start and stop station usage by name
    top_start_station_names = tripdata['start station name'].value_counts().head(top_n)
    top_stop_station_names = tripdata['end station name'].value_counts().head(top_n)
    return top_start_station_names, top_stop_station_names


def plot_top_stations_by_name(station_usage):                                                       # Function to plot pie chart for top stations by name
    plt.figure(figsize=(8, 8))
    plt.pie(station_usage, labels=station_usage.index, autopct='%1.1f%%', startangle=140)
    plt.title('Top 3 Bike Stations by Usage')
    return plt


def plot_top_stations(station_usage, station_ids,
                      bluebike_stations):                                                           # Function to plot pie chart for top stations by ID
    plt.figure(figsize=(8, 8))

    bluebike_stations['Number'] = bluebike_stations['Number'].astype(str)                           # Here is something intresting I did. I decided to figure out how to use astype to convert all station IDs to strings allowing consistent mapping. Then I use a dictionary to map the station ID's to their corresponding name.

    print("Station IDs in 'bluebike_stations':",
          bluebike_stations['Number'].tolist())                                                     # Diagnostic print to check alignment
    print("Station IDs in 'tripdata' being plotted:", station_ids.tolist())

    station_id_to_name = dict(zip(bluebike_stations['Number'], bluebike_stations['Name']))          # Map station IDs to names
    top_station_names = [station_id_to_name.get(str(station_id), "Unknown Station") for station_id in station_ids]

    plt.pie(station_usage, labels=top_station_names, autopct='%1.1f%%', startangle=140)
    plt.title('Top 3 Bike Stations by Usage')
    return plt


def get_station_rankings(bluebike_stations):                                                        # Function to get and display station rankings based on docking ports
    return bluebike_stations.sort_values(by='Total docks', ascending=False)


def main():
    bluebike_stations, tripdata = load_data()

    bluebike_stations.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)

    st.title('Final Project: Bluebike Stations and Trip Analysis')
    st.subheader('By: Leo Susi')
    img = Image.open("download.jpg")
    st.image(img)
    selected_tab = st.sidebar.radio("Navigation", ["Text Questions", "Charts and Graphs", "Map"])

    if selected_tab == "Text Questions":
        st.subheader('Most Popular Start Station on a Specific Date')
        st.write('This input allows the user to add the date and outputs the most popular starting station on the selected day.')

        entered_date = st.text_input('Enter a date (YYYY-MM-DD):', key='date_input')

        if entered_date:
            try:
                selected_date = pd.to_datetime(entered_date)
            except ValueError:
                st.write('Please enter a valid date in the format YYYY-MM-DD.')
            else:
                filtered_trips = tripdata[tripdata['starttime'].str.startswith(str(selected_date.date()))]

                if not filtered_trips.empty:
                    most_popular_start_station = filtered_trips['start station name'].mode().iloc[0]

                    st.write(f"The most popular start station on {selected_date.date()} was {most_popular_start_station}.")
                else:
                    st.write(f"No data found for {selected_date.date()}.")


        st.subheader('Longest Trip Starting from a Station')                                        # Add another section to ask for the longest trip
        st.write('Here you must enter the the bike station name according to the data in the hubway-tripdata file. '
                 'This will produce the longest trip for the specified station along with telling the user the end station.')
        station_name_input2 = st.text_input('Enter the station name for the longest trip:', key='longest_trip_station')

        if station_name_input2:                                                                     # Filter tripdata to select rows where the start station name matches the user input
            filtered_trips = tripdata[tripdata['start station name'] == station_name_input2]

            if not filtered_trips.empty:                                                            # Find the longest trip from the selected station
                longest_trip = filtered_trips.nlargest(1, 'tripduration')

                if not longest_trip.empty:                                                          # Display the longest trip's duration and end station to the user
                    trip_duration_seconds = longest_trip.iloc[0]['tripduration']
                    trip_duration_hours = trip_duration_seconds // 3600
                    trip_duration_minutes = (trip_duration_seconds % 3600) // 60
                    trip_duration_seconds_remainder = trip_duration_seconds % 60

                    end_station = longest_trip.iloc[0]['end station name']

                    st.write(f"The longest trip starting from station {station_name_input2} is "
                             f"{trip_duration_hours} hours, {trip_duration_minutes} minutes, "
                             f"and {trip_duration_seconds_remainder} seconds long, "
                             f"and it ends at station {end_station}.")
                else:
                    st.write(f"No data found for the longest trip starting from station {station_name_input2}.")
            else:
                st.write(f"No data found for station {station_name_input2}.")

        st.subheader('Last Usage of a Bike')                                                        # Add another section to ask for the last usage of a bike
        st.write('The user can enter the desired bike ID. It will then display the time and date of which the '
                 'specified bike was last used.')
        bike_id_input = st.text_input('Enter the bike ID:', key='last_usage_bike_id')

        if st.button('Retrieve Last Usage'):
            if bike_id_input:                                                                       # Convert the input to an integer (assuming bike IDs are integers)
                try:
                    bike_id = int(bike_id_input)
                except ValueError:
                    st.write('Please enter a valid bike ID (an integer).')
                else:                                                                               # Filter tripdata to select rows where the bike ID matches the user input
                    filtered_trips = tripdata[tripdata['bikeid'] == bike_id]

                    if not filtered_trips.empty:                                                    # Convert 'starttime' column to datetime format
                        filtered_trips['starttime'] = pd.to_datetime(filtered_trips['starttime'])

                        last_usage = filtered_trips.nlargest(1, 'starttime')                        # Find the last usage of the bike

                        if not last_usage.empty:                                                    # Display the date and end time of the last usage to the user
                            last_usage_date = last_usage.iloc[0]['stoptime'].split()[0]
                            last_usage_time = last_usage.iloc[0]['stoptime'].split()[1]

                            st.write(
                                f"The bike with ID {bike_id} was last used on {last_usage_date} with a trip end time at {last_usage_time}.")
                        else:
                            st.write(f"No data found for the bike with ID {bike_id}.")
                    else:
                        st.write(f"No data found for the bike with ID {bike_id}.")

        st.subheader('Last Time a Bike ID Was Started at a Station')
        st.write(
            "The user can input the bike ID and station name, and it will display the last time the bike was started at that station.")

        bike_id_input = st.text_input('Enter the bike ID:', key='last_time_bike_id')
        station_name_input = st.text_input('Enter the station name:', key='last_time_station_name')

        if st.button('Retrieve Last Time'):
            if not bike_id_input:
                st.write('Please enter a bike ID.')
            elif not station_name_input:
                st.write('Please enter a station name.')
            else:
                try:
                    bike_id = int(bike_id_input)
                except ValueError:
                    st.write('Please enter a valid bike ID (an integer).')
                else:
                    filtered_trips = tripdata[
                        (tripdata['bikeid'] == bike_id) & (tripdata['start station name'] == station_name_input)]

                    if not filtered_trips.empty:
                        filtered_trips['starttime'] = pd.to_datetime(filtered_trips['starttime'])

                        last_time = filtered_trips.nlargest(1, 'starttime')

                        if not last_time.empty:
                            last_time_date = last_time.iloc[0]['starttime'].strftime('%Y-%m-%d')
                            last_time_time = last_time.iloc[0]['starttime'].strftime('%H:%M:%S')

                            st.write(f"The bike with ID {bike_id} was last started at station {station_name_input} on {last_time_date} at {last_time_time}.")
                        else:
                            st.write(f"No data found for the bike with ID {bike_id} at station {station_name_input}.")
                    else:
                        st.write(f"No data found for the bike with ID {bike_id} at station {station_name_input}.")

    elif selected_tab == "Charts and Graphs":
        st.title('Charts and Graphs')                                                               # Add a section to display the top bike usage chart

        st.subheader('Top Bike Usage')
        st.write('Slider to select the number of top bike IDs to display')
        number_of_bikes = st.slider('Select the number of top bike IDs to display', min_value=1, max_value=20, value=10)
        top_bikes = get_top_bikes(tripdata, top_n=number_of_bikes)
        fig1 = plot_top_bikes(top_bikes)
        st.pyplot(fig1)

        st.subheader('Subscriber vs Customer Usage')                                                # Add a section to display user type chart with checkboxes
        st.write('Checkboxes to select the types of users to display')
        show_subscribers = st.checkbox('Show Subscribers', value=True)
        show_customers = st.checkbox('Show Customers', value=True)

        if show_subscribers or show_customers:
            user_type_count = get_user_type_count(tripdata)
            fig2 = plot_user_type_count(user_type_count, show_subscribers, show_customers)
            st.pyplot(fig2)

        st.subheader('Top Start Stations')  # Add sliders for top start stations
        num_sites_start = st.slider('Select the number of top start stations to display', min_value=1, max_value=10,
                                    value=3)
        start_station_names, stop_station_names = get_station_usage_by_name(tripdata, top_n=num_sites_start)
        fig_start_by_name = plot_top_stations_by_name(start_station_names)
        st.pyplot(fig_start_by_name)

        st.subheader('Top Stop Stations')                                                           # Add sliders for top stop stations
        num_sites_end = st.slider('Select the number of top stop stations to display', min_value=1, max_value=10,
                                  value=3)
        stop_station_names = get_station_usage_by_name(tripdata, top_n=num_sites_end)[1]            # Assign only the second value (stop_station_names)
        fig_stop_by_name = plot_top_stations_by_name(stop_station_names)
        st.pyplot(fig_stop_by_name)

        st.subheader('Bike Usage Over Time')                                                        # Create a line graph of bike usage by date over time
        st.write('This line graph displays the usage of bikes over time.')

        tripdata['starttime'] = pd.to_datetime(tripdata['starttime'])                               # Convert 'starttime' column to datetime format

        bike_usage_by_date = tripdata.groupby(
            tripdata['starttime'].dt.date).size()                                                   # Group trips by date and count the number of trips on each date

        plt.figure(figsize=(12, 6))                                                                 # Plot the line graph
        plt.plot(bike_usage_by_date.index, bike_usage_by_date.values, marker='o', linestyle='-', color='blue')
        plt.title('Bike Usage by Date Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Trips')
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(plt)

        st.subheader('Station Rankings by Docking Ports')                                           # Display station rankings by docking ports
        st.write(
            'The dataframe below demonstrates all of the docking sites in descending order by the total docking amount.')
        station_rankings = get_station_rankings(bluebike_stations)
        st.dataframe(station_rankings[['Name', 'Total docks']])


    elif selected_tab == "Map":

        st.title('Bluebike Stations Map')

        st.write('Here is a map displaying all of the stations with data points within the greater Boston, MA area. '
                 'You can use the drop-down tab to select a certain station. ')
        
        station_selection = st.selectbox("Select a Station:", ['All Stations'] + list(bluebike_stations['Name']))
        if station_selection == 'All Stations':                                                     # Display all stations on the map

            st.map(bluebike_stations[['lat', 'lon']])

        elif station_selection:                                                                     # Filter the station data based on the user's selection

            selected_station = bluebike_stations[bluebike_stations['Name'] == station_selection]

            selected_station = selected_station.rename(columns={'lat': 'LATITUDE', 'lon': 'LONGITUDE'})

            st.map(selected_station)                                                                # Center the map on the selected station's coordinates

            st.subheader(f"Station Information for {station_selection}")

            st.write("Station Name:", selected_station['Name'].values[0])
            st.write("Latitude:", selected_station['LATITUDE'].values[0])
            st.write("Longitude:", selected_station['LONGITUDE'].values[0])


if __name__ == '__main__':
    main()

