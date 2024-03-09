# Release Note: Search Mechanism

## Introduction
The search mechanism is a powerful feature introduced to enhance the user experience by allowing efficient and relevant searches through documentation. It leverages advanced AI techniques to understand user queries and fetch pertinent documentation, making information discovery seamless and intuitive.

## Features
- **Minimum Score Threshold**: Users can specify a minimum score for search results, ensuring that only the most relevant documentation is returned.
- **Result Limit**: To manage the volume of information, users have the option to limit the number of results returned by the search.

## AI Module Processing
The AI module (`upsonic_on_prem/utils/ai/ai.py`) is at the heart of the search mechanism. It processes user queries by:
- Generating embeddings for both the documentation and the query using a pre-trained model.
- Utilizing a vectorstore for similarity search to identify documentation that closely matches the query based on the embeddings.
- Returning documentation that meets the specified minimum score threshold and within the set limit for the number of results.

## Django View Handling
The Django view (`upsonic_on_prem/dash/app/views.py`) plays a crucial role in handling search requests. Upon receiving a POST request with the search parameters, it:
- Extracts the query, minimum score, and result limit from the request.
- Calls the AI module to perform the search with the provided parameters.
- Passes the search results to the template for display to the user.

## User Interface
The search functionality is made accessible through a user-friendly interface, which includes:
- A **search form** where users can input their query, specify a minimum score, and set a limit on the number of results.
- A **results display section** in the template (`upsonic_on_prem/dash/app/templates/search.html`) that showcases the search outcomes, including documentation links and relevance scores.

## How to Use
To perform a search:
1. Navigate to the search page.
2. Enter your query in the search bar.
3. Optionally, set a minimum score and limit the number of results.
4. Click the "Search" button to initiate the search.
5. Review the results displayed on the page to find the most relevant documentation.

This intuitive search mechanism is designed to streamline the process of finding relevant documentation, making it easier for users to access the information they need.
