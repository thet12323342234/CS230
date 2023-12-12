import streamlit as st                                                                              # Import the Streamlit library for creating the web app
import pandas as pd                                                                                 # Import the Pandas library for data manipulation
import matplotlib.pyplot as plt                                                                     # Import Matplotlib for data visualization


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

def plot_user_type_count(user_type_count, show_subscribers=True, show_customers=True):              # Updated function to plot user type count (subscribers vs customers)
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

def plot_top_stations(station_usage, station_ids, bluebike_stations):                               # Function to plot pie chart for top stations by ID
    plt.figure(figsize=(8, 8))

    bluebike_stations['Number'] = bluebike_stations['Number'].astype(str)                           # Convert all station IDs to strings for consistent mapping

    print("Station IDs in 'bluebike_stations':", bluebike_stations['Number'].tolist())              # Diagnostic print to check alignment
    print("Station IDs in 'tripdata' being plotted:", station_ids.tolist())

    station_id_to_name = dict(zip(bluebike_stations['Number'], bluebike_stations['Name']))          # Map station IDs to names
    top_station_names = [station_id_to_name.get(str(station_id), "Unknown Station") for station_id in station_ids]

    plt.pie(station_usage, labels=top_station_names, autopct='%1.1f%%', startangle=140)
    plt.title('Top 3 Bike Stations by Usage')
    return plt

def get_station_rankings(bluebike_stations):                                                        # Function to get and display station rankings based on docking ports
    return bluebike_stations.sort_values(by='Total docks', ascending=False)

def main():                                                                                         # The main function where the Streamlit web app is defined
    bluebike_stations, tripdata = load_data()                                                       # Load data using the cached function

    bluebike_stations.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)         # Rename columns for Streamlit map compatibility

    st.title('Final Project By: Leo Susi- Bluebike Stations and Trip Analysis')                     # Streamlit app name

    selected_tab = st.sidebar.radio("Navigation", ["Text Questions", "Charts and Graphs", "Map"])   # Sidebar with tabs

    if selected_tab == "Text Questions":                                                            # Add a section to ask the user for the station name
        st.subheader('Most Used Bike Time for a Station')
        st.write('Here you must enter the the bike station name according to the data in the hubway-tripdata file.')
        station_name_input = st.text_input('Enter the station name:', key='most_used_bike_station')

        if station_name_input:                                                                      # Filter tripdata to select rows where the start station name matches the user input
            filtered_trips = tripdata[tripdata['start station name'] == station_name_input]

            if not filtered_trips.empty:                                                            # Calculate the most used bike time for the selected station
                most_used_time = filtered_trips['starttime'].mode().iloc[0]

                st.write(f"The most used bike time for station '{station_name_input}' is: {most_used_time}")
            else:
                st.write(f"No data found for station '{station_name_input}'")

        st.subheader('Longest Trip Starting from a Station')                                        # Add another section to ask for the longest trip
        st.write('Here you must enter the the bike station name according to the data in the hubway-tripdata file.'
                 'This will produce the longest trip for the specified station.')
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

                    st.write(f"The longest trip starting from station '{station_name_input2}' is "
                             f"{trip_duration_hours} hours, {trip_duration_minutes} minutes, "
                             f"and {trip_duration_seconds_remainder} seconds long, "
                             f"and it ends at station '{end_station}'.")
                else:
                    st.write(f"No data found for the longest trip starting from station '{station_name_input2}'.")
            else:
                st.write(f"No data found for station '{station_name_input2}'")

        st.subheader('Last Usage of a Bike')                                                        # Add another section to ask for the last usage of a bike
        st.write('The user can enter the bike ID which is desired. It will then display the most popular time of which the '
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
                                f"The bike with ID '{bike_id}' was last used on {last_usage_date} with a trip end time at {last_usage_time}.")
                        else:
                            st.write(f"No data found for the bike with ID '{bike_id}'.")
                    else:
                        st.write(f"No data found for the bike with ID '{bike_id}'.")

        st.subheader('Last Location of a Bike at a Station')                                        # Add another section to ask for the last location of a bike at a station
        st.write(
            "The user can input the bike ID, and it will display which station the bike was last used, along with the date,"
            "and the end time of the bike's use")
        bike_id_input = st.text_input('Enter the bike ID:', key='last_location_bike_id')
        station_name_input = st.text_input('Enter the station name:', key='last_location_station_name')

        if st.button('Retrieve Last Location'):
            if bike_id_input and station_name_input:                                                # Convert the input to an integer (assuming bike IDs are integers)
                try:
                    bike_id = int(bike_id_input)
                except ValueError:
                    st.write('Please enter a valid bike ID (an integer).')
                else:                                                                               # Filter tripdata to select rows where the bike ID and station name match the user input
                    filtered_trips = tripdata[
                        (tripdata['bikeid'] == bike_id) & (tripdata['end station name'] == station_name_input)]

                    if not filtered_trips.empty:                                                    # Convert 'stoptime' column to datetime format
                        filtered_trips['stoptime'] = pd.to_datetime(filtered_trips['stoptime'])

                        last_location = filtered_trips.nlargest(1, 'stoptime')                      # Find the last location of the bike at the specified station

                        if not last_location.empty:                                                 # Display the date and time when the bike was last located at the station to the user
                            last_location_date = last_location.iloc[0]['stoptime'].strftime('%Y-%m-%d')
                            last_location_time = last_location.iloc[0]['stoptime'].strftime('%H:%M:%S')

                            st.write(
                                f"The bike with ID '{bike_id}' was last located at station '{station_name_input}' on {last_location_date} at {last_location_time}.")
                        else:
                            st.write(f"No data found for the bike with ID '{bike_id}' at station '{station_name_input}'.")
                    else:
                        st.write(f"No data found for the bike with ID '{bike_id}' at station '{station_name_input}'.")

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

        st.subheader('Top Start Stations')                                                          # Add sliders for top start stations
        num_sites_start = st.slider('Select the number of top start stations to display', min_value=1, max_value=10, value=3)
        start_station_names, stop_station_names = get_station_usage_by_name(tripdata, top_n=num_sites_start)
        fig_start_by_name = plot_top_stations_by_name(start_station_names)
        st.pyplot(fig_start_by_name)

        st.subheader('Top Stop Stations')                                                           # Add sliders for top stop stations
        num_sites_end = st.slider('Select the number of top stop stations to display', min_value=1, max_value=10, value=3)
        stop_station_names = get_station_usage_by_name(tripdata, top_n=num_sites_end)[1]            # Assign only the second value (stop_station_names)
        fig_stop_by_name = plot_top_stations_by_name(stop_station_names)
        st.pyplot(fig_stop_by_name)

        st.subheader('Bike Usage Over Time')                                                        # Create a line graph of bike usage by date over time
        st.write('This line graph displays the usage of bikes over time.')

        tripdata['starttime'] = pd.to_datetime(tripdata['starttime'])                               # Convert 'starttime' column to datetime format

        bike_usage_by_date = tripdata.groupby(tripdata['starttime'].dt.date).size()                 # Group trips by date and count the number of trips on each date

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
        st.write('Here is a map displaying all of the stations with data points within the greater Boston, MA area.')
        st.map(bluebike_stations[['lat', 'lon']])

if __name__ == '__main__':
    main()
