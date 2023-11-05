from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import requests
import logging

logger = logging.getLogger('django')

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

def search_form(request):
    return render(request, 'search/search_form.html')

def search(request):
    results = []

    if request.method == 'POST':
        query = request.POST.get('query')
        api_key = settings.GOOGLE_API_KEY
        cx = settings.GOOGLE_CX

        logger.debug("Query: %s", query)

        try:
            results = google_custom_search(api_key, cx, query)
        except Exception as e:
            # Handle the exception gracefully and provide an informative response to the client
            return JsonResponse({"error": "An error occurred while processing your request."}, status=500)

    return render(request, 'search/results.html', {'results': results})
