import requests


def search_bing_maps(api_key, query)
  #API endpoint for Bing Maps API Local Search
  endpoint = "https://dev.virtualearth.net/REST/v1/LocalSearch/"

  params = {
  'query': query,
  'userCircularMapView': location,
  'key' : key
  }
  #make request to the API
  response = requests.get(endpoint, params=params)

  if response.status_code == 200:
    data = response.json()

    for resource in data['resourceSets'][0]['resources']:
      print("Name:", resource['name'])
      print("Website:", resource['Website'])
      print("Address:", resource['address'])
      print("Phone Number:", resource['PhoneNumber'])

  else:
    print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
  api_key = 'AljWRZaoHZnN5BFLuSNUROkPiOCcENdXKPymfc3ZTEZvrhRF1ERohuvlSonkFe_c'
  'userCircularMapView' = '35.493583,-97.521591,5000' #the Drake OKC latitude longtitude plus a radius in meters
  search_query = 'coffee'
  search_bing_maps(api_key, search_query)
