# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import logging
from serpapi import BingSearch
import requests

logger = logging.getLogger('django')

# Function to make a request to SerpApi
def serpapi_search(query):
    api_key = settings.SERPAPI_API_KEY  

    params = {
        "q": query,
        "api_key": api_key,
        "num": 40
        # You can add more parameters here as needed
    }

    try:
        search = BingSearch(params)
        results = search.get_dict()

        return results.get("organic_results", [])  # Extract organic search results

    except Exception as e:
        logger.error("An error occurred while querying SerpApi: %s", e)
        return []

# google_custom_search function
def google_custom_search(api_key, cx, query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        results = []

        if 'items' in data:
            search_results = data['items']
            for result in search_results:
                title = result.get("title", 'No Title')
                link = result.get("link", 'No Link')
                snippet = result.get("snippet", 'No Snippet')
                results.append({"title": title, "link": link, "snippet": snippet})

        return results

    except requests.exceptions.RequestException as e:
        logger.error("An error occurred: %s", e)
        raise  # Reraise the exception
    
def remove_duplicates(results):
    unique_results = []
    seen_links = set()

    for result in results:
        link = result.get("link")
        if link not in seen_links:
            seen_links.add(link)
            unique_results.append(result)

    return unique_results


# Function to integrate results from Google Custom Search and SerpApi
def integrate_multiple_apis(query):
    results = []

    # Call functions for Google Custom Search and SerpApi to get results
    google_results = google_custom_search(settings.GOOGLE_API_KEY, settings.GOOGLE_CX, query)
    serpapi_results = serpapi_search(query)

    # Combine results from different APIs
    results.extend(google_results)
    results.extend(serpapi_results)
    
    # Remove duplicates based on the "link" key
    unique_results = remove_duplicates(results)

    # You can sort or filter the results here if needed

    return unique_results

def search_form(request):
    return render(request, 'search/search_form.html')

def search(request):
    results = []

    if request.method == 'POST':
        query = request.POST.get('query')

        logger.debug("Query: %s", query)

        try:
            results = integrate_multiple_apis(query)
        except requests.exceptions.RequestException as google_error:
            logger.error("Google Custom Search error: %s", google_error)
            return JsonResponse({"error": "An error occurred while querying Google Custom Search."}, status=500)
        except Exception as serpapi_error:
            logger.error("SerpApi error: %s", serpapi_error)
            return JsonResponse({"error": "An error occurred while querying SerpApi."}, status=500)

    return render(request, 'search/results.html', {'results': results})
