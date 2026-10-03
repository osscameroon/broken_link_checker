from bs4 import BeautifulSoup
import requests

# test_site_url = "https://testsite.come/"
test_site_url = input("Enter Website Link You Want To Test: --> http://test.com")
  
# Check if a link is reachable 
def is_reachable(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError if unreachable
        return True
    except requests.exceptions.HTTPError:
        return False
    except requests.exceptions.RequestException:
        return False
      
if is_reachable(test_site_url):
  response = requests.get(test_site_url)
  print("--- Working on: ", test_site_url)
    
  # Parse the HTML content
  soup = BeautifulSoup(response.text, 'html.parser')
  
  print("--- Getting all links")
  # Extract all links
  links = []
  for link in soup.find_all('a', href=True):
      links.append(link['href'])
  
  print(len(links))
  print("--- Getting unique links")
  # remove duplicated links from the list of links
  unique_list = list(set(links))
  
  print(len(unique_list))
  print("--- Convert all links URLs into valid ")
  # Sanitize all links to be valid URL addresses
  valid_urls = []
  for link in unique_list:
    if not link.startswith(('http://', 'https://')):
      valid_link = test_site_url + link
    else:
      valid_link = link
      
    valid_urls.append(valid_link)
  
  for url in valid_urls:
    if is_reachable(url):
        print(f"{url} is reachable")
    else:
        print(f"{url} is not reachable")   

  # Print or save the links
  # for link in valid_urls:
  #     print(link)   

else:
  print(f"{test_site_url} is not reachable. Please Verify And Try Again")  
