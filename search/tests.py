#from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from unittest.mock import patch

from django.urls import reverse
from search.views import integrate_multiple_apis

#tests case for the views.py
class SearchViewTests(TestCase):
    @patch('search.views.google_custom_search')
    @patch('search.views.serpapi_search')
    def test_integrate_multiple_apis(self, mock_serpapi_search, mock_google_custom_search):
        # Mock the results from SerpApi and Google Custom Search
        mock_serpapi_search.return_value = [{"title": "SerpApi Result", "link": "https://example.com/serpapi", "snippet": "Snippet"}]
        mock_google_custom_search.return_value = [{"title": "Google Result", "link": "https://example.com/google", "snippet": "Snippet"}]

        # Call the function with a sample query
        results = integrate_multiple_apis("test query")

        # Check if the function combines results and removes duplicates
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Google Result")
        self.assertEqual(results[1]["title"], "SerpApi Result")
        self.assertEqual(results[0]["link"], "https://example.com/google")
        self.assertEqual(results[1]["link"], "https://example.com/serpapi")

#test case for the urls.py file
    def test_search_form_view(self):
        response = self.client.get(reverse('search_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search_form.html')

    def test_search_view(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/results.html')