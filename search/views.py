# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import logging
from serpapi import BingSearch
import requests
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Query, SearchResult

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

@transaction.atomic
def store_query_and_results(query_text, search_results):
    # Create a Query instance and save it to the database
    query_instance = Query.objects.create(query_text=query_text)

    # Create a list of SearchResult instances
    search_results_instances = [
        SearchResult(
            query=query_instance,
            title=result.get("title", ""),
            link=result.get("link", ""),
            snippet=result.get("snippet", "")
        )
        for result in search_results
    ]

    # Bulk create the SearchResult instances
    SearchResult.objects.bulk_create(search_results_instances)

def remove_duplicates(results):
    unique_results = []
    seen_links = set()

    for result in results:
        link = result.get("link")
        if link not in seen_links:
            seen_links.add(link)
            unique_results.append(result)

    return unique_results

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

    return unique_results, query

def search_form(request):
    return render(request, 'search/search_form.html')

def search(request):
    query = ""
    results = []

    if request.method == 'POST':
        query = request.POST.get('query')

        logger.debug("Query: %s", query)

        try:
            results, query = integrate_multiple_apis(query)
            store_query_and_results(query, results)
        except requests.exceptions.RequestException as api_error:
            logger.error("API error: %s", api_error)
            return JsonResponse({"error": f"An error occurred while querying the API: {api_error}"}, status=500)
        except Exception as error:
            logger.error("Error: %s", error)
            return JsonResponse({"error": f"An error occurred: {error}"}, status=500)

    # Paginate the results if a query is present
    if query:
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 10)  # Show 10 results per page

        try:
            paginated_results = paginator.page(page)
        except PageNotAnInteger:
            paginated_results = paginator.page(1)
        except EmptyPage:
            paginated_results = paginator.page(paginator.num_pages)
    else:
        paginated_results = []

    return render(request, 'search/results.html', {'results': paginated_results, 'query': query})
