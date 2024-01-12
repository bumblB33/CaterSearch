import csv
import requests
import tkinter as tk

# Variables used to build the list of Bing Maps search
search_terms = ["Law+Firm"] # temporarily excluding other parameters for testing brevity
#, "Architecture", "Architect", "Manufacturing", "Manufacturer", "Distribution+Center", \
#"Law+Office", "Lawyer", "Catholic+Schools", "Private+Schools", "Public+Schools", "Engineering"]

def search_locations(api_key, restaurant_text, location_text, csv_writer):
    # First search to obtain latitude and longitude
    endpoint = "https://dev.virtualearth.net/REST/v1/Locations/"
    query = f"{restaurant_text} {location_text}"
    params = {
        'q': query,
        'key': api_key
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        data = response.json()

        if data.get('resourceSets'):
            location_info = data['resourceSets'][0]['resources'][0]
            latitude = location_info['point']['coordinates'][0]
            longitude = location_info['point']['coordinates'][1]
            geocode_points = {
                "latitude": latitude,
                "longitude": longitude
            }

            # Convert radius from miles to meters
            radius_miles = float(radius_var.get())
            max_radius_meters = 5000

            # Perform searches with varying origin points
            perform_searches(api_key, geocode_points, radius_miles, csv_writer)

        else:
            print("Error: Location not found.")

    else:
        print(f"Error: {response.status_code}, {response.text}")

def perform_searches(api_key, geocode_points, max_radius_miles, csv_writer):
    # Calculate the number of segments
    num_segments = int(max_radius_miles / 5)  # Assuming each segment covers 5 miles

    for i in range(num_segments):
        # Adjust the origin points for each segment
        new_latitude = geocode_points['latitude'] + i * 0.045  # Adjust based on your needs
        new_longitude = geocode_points['longitude'] + i * 0.045  # Adjust based on your needs

        # Convert radius from miles to meters
        radius_meters = min(5 * 1609.344, 5000)  # Assuming each segment covers 5 miles

        # Build the search query for each segment
        search_query = f"{new_latitude},{new_longitude},{radius_meters}"
        search_bing_maps(api_key, search_query, csv_writer)

def search_bing_maps(api_key, search_query, csv_writer):
    # Use the search_terms list as query terms
    for query_term in search_terms:
        endpoint = "https://dev.virtualearth.net/REST/v1/LocalSearch/"
        params = {
            'query': query_term,
            'userCircularMapView': search_query,
            'key': api_key
        }

        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            data = response.json()
            print(data)

            if data.get('resourceSets', []):
                for resource in data['resourceSets'][0].get('resources', []):
                    name = resource.get('name', 'N/A')
                    website = resource.get('Website', 'N/A')
                    phone_number = resource.get('PhoneNumber', 'N/A')
                    address_info = resource.get('Address', {})
                    formatted_address = address_info.get('formattedAddress', 'N/A')

                    # Combine address components
                    address = f"{formatted_address}"

                    # Write the data to CSV
                    csv_writer.writerow([name, website, phone_number, address])


            else:
                print("No results found.")

        else:
            print(f"Error: {response.status_code}, {response.text}")

def create_web_string():
    restaurant_text = restaurant_entry.get()
    location_text = location_entry.get()

    # Specify the CSV file name
    csv_file_name = "lead_results.csv"

    # Open the CSV file in write mode
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)

        # Write header to the CSV file
        csv_writer.writerow(["Name", "Website", "Phone Number", "Address"])

        # Call the search_locations function with the CSV writer
        search_locations(api_key, restaurant_text, location_text, csv_writer)


if __name__ == "__main__":
    api_key = 'AljWRZaoHZnN5BFLuSNUROkPiOCcENdXKPymfc3ZTEZvrhRF1ERohuvlSonkFe_c'

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
