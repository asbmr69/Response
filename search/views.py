
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
# search/views.py

import requests

def google_custom_search(api_key, cx, query):
    # The same google_custom_search function as in the Flask example
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)

        data = response.json()
        results=[]
        if 'items' in data:
            search_results = data['items']
            for result in search_results:
                # Extract and format relevant information from each search result
                title = result.get("title", 'No Title')
                link = result.get("link", 'No Link')
                snippet = result.get("snippet", 'No Snippet')
                results.append({"title": title, "link": link,"snippet":snippet})

        return results


    except requests.exceptions.RequestException as e:
        return print(f"An error occurred: {e}")


def search_form(request):
    # This view renders the search form
    return render(request, 'search/search_form.html')


def search(request):
    results = []

    if request.method == 'POST':
        query = request.POST['query']
        api_key = "AIzaSyCZMgwmv-mF9O_JQjuK6cmTYJB-hIBzlOA"
        cx = "47404471b11724b83"
        print(f"Query: {query}")
        results = google_custom_search(api_key, cx, query)
        print(results)

    return render(request,'search/results.html',{'results': results})
    
   
