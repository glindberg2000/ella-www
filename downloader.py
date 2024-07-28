import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def save_file(url, directory):
    """Download and save a file from a URL, preserving the original file name."""
    try:
        # Get the content of the file
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Parse the URL to get the file name
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)

        # Avoid trying to save a directory
        if not file_name:
            print(f"Skipping download for directory URL: {url}")
            return None

        # Ensure directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the file
        file_path = os.path.join(directory, file_name)
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {file_name}")
        return file_path
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None


def download_assets(html_content, base_url, download_dir):
    """Download all assets linked in the HTML content and rewrite the links."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Function to rewrite URLs
    def rewrite_url(tag, attr, subdir):
        url = tag.get(attr)
        if url:
            asset_url = urljoin(base_url, url)
            local_file = save_file(asset_url, os.path.join(download_dir, subdir))
            if local_file:
                tag[attr] = os.path.relpath(local_file, download_dir)

    # Download images
    for img in soup.find_all("img"):
        rewrite_url(img, "src", "images")
        if img.get("srcset"):
            srcset = img["srcset"].split(",")
            new_srcset = []
            for src in srcset:
                parts = src.strip().split()
                new_url = save_file(
                    urljoin(base_url, parts[0]), os.path.join(download_dir, "images")
                )
                if new_url:
                    new_srcset.append(
                        f"{os.path.relpath(new_url, download_dir)} {' '.join(parts[1:])}"
                    )
            img["srcset"] = ", ".join(new_srcset)

    # Download videos
    for video in soup.find_all("video"):
        rewrite_url(video, "src", "videos")
        for source in video.find_all("source"):
            rewrite_url(source, "src", "videos")

    # Download CSS and JS files
    for tag in soup.find_all(["link", "script"]):
        if tag.name == "link" and tag.get("rel") == ["stylesheet"]:
            rewrite_url(tag, "href", "css")
        elif tag.name == "script" and tag.get("src"):
            local_file = rewrite_url(tag, "src", "js")
            if local_file and local_file.endswith(".js"):
                map_file = local_file + ".map"
                map_url = urljoin(base_url, os.path.basename(map_file))
                save_file(map_url, os.path.join(download_dir, "js"))

        elif tag.name == "link" and "icon" in tag.get("rel", []):
            rewrite_url(tag, "href", "icons")

    # Download linked files (e.g., PDFs)
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and (
            href.endswith(".pdf") or href.endswith(".docx") or href.endswith(".pptx")
        ):
            rewrite_url(link, "href", "docs")

    return str(soup)


def download_site(base_url, download_dir):
    """Download the HTML and all assets of a site."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    try:
        # Get the main HTML content
        response = requests.get(base_url)
        response.raise_for_status()
        html_content = response.text

        # Download all assets and rewrite the HTML content
        updated_html_content = download_assets(html_content, base_url, download_dir)

        # Save the updated HTML file
        with open(
            os.path.join(download_dir, "index.html"), "w", encoding="utf-8"
        ) as file:
            file.write(updated_html_content)
        print("Saved: index.html")
    except requests.RequestException as e:
        print(f"Failed to download site: {e}")


# Example usage
base_url = "http://www.ella-ai-care.com"
download_dir = "./"
download_site(base_url, download_dir)