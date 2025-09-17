# Streamlit Leads Finder App

**Site:** [Link to WebApp](https://lead-generator-scraping.streamlit.app/)

## Overview  
The **Streamlit Leads Finder App** helps you discover business leads in a specific industry and city using **SerpAPI**.  
It retrieves company details (name, website, location, etc.) directly from Google results.  
If a company website is available, the app performs an **additional scraping step** to extract:  
- Public email addresses  
- Phone numbers  
- Links to social media (e.g., LinkedIn, Facebook, Instagram)  

All results are stored in a Pandas DataFrame and displayed both in an interactive table and on a map inside Streamlit.  

---

## How It Works  
1. **User Input**  
   - Choose the industry/sector.  
   - Choose the city/region.  

2. **Lead Discovery via SerpAPI**  
   - Queries Google search results with the provided keywords.  
   - Retrieves structured data: business names, addresses, websites, etc.  

3. **Website Scraping (optional step)**  
   - If a website is found, the app crawls the page to collect:  
     - Public email addresses  
     - Phone numbers  
     - Social media links (LinkedIn, Facebook, Instagram, etc.)  

4. **Data Consolidation**  
   - All results are merged into a **Pandas DataFrame**.  
   - Leads can be filtered and exported if needed.  

5. **Visualization in Streamlit**  
   - **Table View** → browse and filter all results.  
   - **Map View** → businesses plotted on a map with geolocation.  

---

## Technical Requirements  
- **Language**: Python  
- **Framework**: [Streamlit](https://streamlit.io/)  
- **Core Libraries**:  
  - `pandas` → data handling  
  - `requests` → web requests  
  - `BeautifulSoup` → website scraping  
  - `re` → regex for emails, phones, and social media links  
  - `serpapi` → Google search results API  

---

## Non-Technical Considerations  
- Requires a valid **SerpAPI key**.  
- Scraping is limited to **publicly available data**.  

---

## Example Use Case  
- Search for **"lawyers in San Francisco"**.  
- SerpAPI returns business names, websites, and addresses.  
- For each website found, the app scrapes for contact emails, phone numbers, and LinkedIn profiles.  
- Results are shown in a searchable table and displayed on a map of San Francisco.  
