import requests
from bs4 import BeautifulSoup
from base64 import b64decode

BASE_URL = "https://aniworld.to"
COOKIES = {"aniworld_session": "xxxxxxxxx"}


def get_episode_page(url, cookies):
    """Fetches the episode page content."""
    response = requests.get(url, cookies=cookies)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None


def parse_host_links(content):
    """Parses host links from the episode page."""
    soup = BeautifulSoup(content, "html.parser")
    file_code_input = soup.find_all("a", {"target": "_blank", "class": "watchEpisode"})
    host_links = {}

    for link in file_code_input:
        host_name = link.find("h4").text.strip()
        href_link = link.get("href")
        host_links[host_name] = href_link

    return host_links


def get_redirect_url(host_link):
    """Fetches the redirected URL for the selected host."""
    response = requests.get(host_link)
    for line in response.text.splitlines():
        if "window.location.href = '" in line:
            e_url = line.strip().split(" = '")[1].strip("';")
            return e_url
    return None


def get_video_url(e_url):
    """Fetches the direct MP4 video URL from the redirect page."""
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://voe.sx/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
    }
    response = requests.get(e_url, headers=headers)
    for line in response.text.splitlines():
        if "'mp4'" in line:
            mp4_url_encoded = line.strip().split(": ")[1].strip("'").strip("',")
            mp4_url = b64decode(mp4_url_encoded).decode()
            return mp4_url
    return None


def download_video(mp4_url, filename):
    """Downloads the MP4 video file."""
    response = requests.get(mp4_url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"Downloaded video as {filename}")
    else:
        print("Failed to download video")


def main(episode_url):
    content = get_episode_page(episode_url, COOKIES)
    if not content:
        return

    host_links = parse_host_links(content)
    redirect_provider = 'VOE'
    if "VOE" not in host_links:
        print("VOE link not found.")
        redirect_provider = host_links[list(host_links.keys())[0]]

    link = f"{BASE_URL}{host_links[redirect_provider]}"
    e_url = get_redirect_url(link)
    if not e_url:
        print("Failed to retrieve the redirect URL.")
        return

    mp4_url = get_video_url(e_url)
    if not mp4_url:
        print("Failed to retrieve the MP4 URL.")
        return
    title = "_".join(episode_url.split("/")[-3:])
    print(title)
    download_video(mp4_url, title + ".mp4")


if __name__ == "__main__":
    episode_url = input("Enter Episode URL: ")
    main(episode_url)
