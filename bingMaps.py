import csv
import math
import requests
import tkinter as tk

# Bing Maps API key
api_key = 'AljWRZaoHZnN5BFLuSNUROkPiOCcENdXKPymfc3ZTEZvrhRF1ERohuvlSonkFe_c'

def get_geocode(api_key, restaurant_text, location_text):
    # Query Bing Maps API to obtain latitude and longitude for the given location
    endpoint = "https://dev.virtualearth.net/REST/v1/Locations"
    query = f"{restaurant_text}, {location_text}"
    params = {'q': query, 'key': api_key}

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        data = response.json()

        if data.get('resourceSets'):
            location_info = data['resourceSets'][0]['resources'][0]
            latitude = location_info['point']['coordinates'][0]
            longitude = location_info['point']['coordinates'][1]

            return latitude, longitude
        else:
            print(f"Error: Location not found. Response: {data}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

    return None  # Return None in case of error

def create_web_string():
    # Get user input from GUI
    restaurant_text = restaurant_entry.get()
    location_text = location_entry.get()
    radius_miles = float(radius_var.get())

    # Get latitude and longitude for the given location
    geocode_result = get_geocode(api_key, restaurant_text, location_text)

    # Define search_query outside the if block
    search_query = ""

    # Define csv_writer before the loop
    csv_file_name = "lead_results.csv"
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)

        # Write header to the CSV file
        csv_writer.writerow(["Name", "Website", "Phone Number", "Address"])

        if geocode_result:
            center_latitude, center_longitude = geocode_result

            # Calculate square corners
            sw_lat, sw_lon, ne_lat, ne_lon = calculate_square_corners(center_latitude, center_longitude, radius_miles)

            # Construct search query
            search_query = f"{center_latitude},{center_longitude},{radius_miles}"

            # Iterate over search terms and call search_bing_maps for each term
            for query_term in ["Law Firm", "Architecture", "Architect", "Manufacturing", "Manufacturer",
                           "Distribution Center", "Law Office", "Lawyer", "Catholic Schools",
                           "Private Schools", "Public Schools", "Engineering"]:
                search_bing_maps(api_key, query_term, center_latitude, center_longitude, radius_miles, csv_writer)

def calculate_square_corners(center_latitude, center_longitude, radius_miles):
    # Calculate the coordinates of the square corners
    earth_radius = 3959.0  # Earth radius in miles

    # Calculate the actual distance for latitude and longitude
    lat_distance = (radius_miles / earth_radius) * (180 / math.pi)
    lon_distance = (radius_miles / earth_radius) / math.cos(math.radians(center_latitude)) * (180 / math.pi)

    # Calculate the square corners
    sw_lat = center_latitude - lat_distance
    sw_lon = center_longitude - lon_distance
    ne_lat = center_latitude + lat_distance
    ne_lon = center_longitude + lon_distance

    print(f"lat_distance: {lat_distance}, lon_distance: {lon_distance}")
    print(f"sw_lat: {sw_lat}, sw_lon: {sw_lon}, ne_lat: {ne_lat}, ne_lon: {ne_lon}")


    return sw_lat, sw_lon, ne_lat, ne_lon



def search_bing_maps(api_key, query_term, center_latitude, center_longitude, radius_miles, csv_writer):
    # Search Bing Maps API for the given query term within the specified radius
    endpoint = "https://dev.virtualearth.net/REST/v1/LocalSearch/"
    total_results = 0

    print(f"Query Term: {query_term}")
    print(f"Center Latitude: {center_latitude}, Center Longitude: {center_longitude}")

    # Construct bounding box for the search area
    bounding_box = f'{center_latitude - radius_miles},{center_longitude - radius_miles},' \
    f'{center_latitude + radius_miles},{center_longitude + radius_miles}'
    print(f"Bounding Box: {bounding_box}")

    # Include bounding box in the URL
    params = {'query': f'{query_term}', 'bbox': bounding_box, 'key': api_key}
    response = requests.get(endpoint, params=params)
    print(f"API Request URL: {response.url}")

    if response.status_code == 200:
        data = response.json()

        if data.get('resourceSets', []):
            current_results = data['resourceSets'][0].get('resources', [])
            total_results += len(current_results)
            total_results += len(current_results)
            for resource in current_results:
                name = resource.get('name', 'N/A')
                website = resource.get('Website', 'N/A')
                phone_number = resource.get('PhoneNumber', 'N/A')
                address_info = resource.get('Address', {})
                formatted_address = address_info.get('formattedAddress', 'N/A')

                if 'point' in resource:
                    result_latitude = resource['point']['coordinates'][0]
                    result_longitude = resource['point']['coordinates'][1]
                    distance = calculate_distance(center_latitude, center_longitude, result_latitude, result_longitude)

                    # Include result only if within the specified radius
                    if distance <= radius_miles:
                        # Combine address components
                        address = f"{formatted_address}"
                        csv_writer.writerow([name, website, phone_number, address])


                    else:
                        print(f"Warning: 'point' not found in resource")

        else:
            print("No results found.")

    else:
        print(f"Error: {response.status_code}, {response.text}")

    print(f"Total Results: {total_results}")

def calculate_distance(lat1, lon1, lat2, lon2):
    # Calculate distance between two points on Earth using Haversine formula
    earth_radius = 3959.0  # Earth radius in miles

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = earth_radius * c

    return distance


if __name__ == "__main__":
    # GUI setup
    root = tk.Tk()
    root.title("Lead Search Tool")
    root.geometry("400x200")  # Width x Height

    # Restaurant Entry
    restaurant_label = tk.Label(root, text="Enter Client Restaurant Name:")
    restaurant_label.pack()

    restaurant_entry = tk.Entry(root)
    restaurant_entry.pack()

    # Location Entry
    location_label = tk.Label(root, text="Enter Client City and State:")
    location_label.pack()

    location_entry = tk.Entry(root)
    location_entry.pack()

    # Radius Dropdown
    radius_label = tk.Label(root, text="Select Radius in Miles:")
    radius_label.pack()

    radius_var = tk.StringVar(root)
    radius_var.set("10")  # Default radius
    radius_dropdown = tk.OptionMenu(root, radius_var, "5", "10", "15", "20", "25", "30")
    radius_dropdown.pack()

    # Search Button
    search_button = tk.Button(root, text="Search", command=create_web_string)
    search_button.pack()

    # Run the Tkinter event loop
    root.mainloop()
