import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger('security')


def fetch_link_preview(url, timeout=15):
    """
    Fetch Open Graph metadata from a URL for link preview.
    Returns dict with title, description, image, and video URLs.
    """
    try:
        # Enhanced headers to mimic a real browser more closely
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, verify=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract Open Graph metadata
        metadata = {
            'title': None,
            'description': None,
            'image': None,
            'video': None,
            'url': url
        }

        # Try Open Graph tags first
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['title'] = og_title.get('content', '')

        og_description = soup.find('meta', property='og:description')
        if og_description:
            metadata['description'] = og_description.get('content', '')

        og_image = soup.find('meta', property='og:image')
        if og_image:
            metadata['image'] = og_image.get('content', '')

        og_video = soup.find('meta', property='og:video')
        if og_video:
            metadata['video'] = og_video.get('content', '')

        # Fallback to Twitter Card tags
        if not metadata['title']:
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title:
                metadata['title'] = twitter_title.get('content', '')

        if not metadata['description']:
            twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            if twitter_desc:
                metadata['description'] = twitter_desc.get('content', '')

        if not metadata['image']:
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image:
                metadata['image'] = twitter_image.get('content', '')

        # Fallback to standard HTML tags
        if not metadata['title']:
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.string

        if not metadata['description']:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['description'] = meta_desc.get('content', '')

        # Clean up and validate URLs
        if metadata['image'] and not metadata['image'].startswith(('http://', 'https://')):
            # Handle relative URLs
            from urllib.parse import urljoin
            metadata['image'] = urljoin(url, metadata['image'])

        logger.info(f"Successfully fetched link preview for: {url}")
        return metadata

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching link preview for: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching link preview for {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching link preview for {url}: {str(e)}")
        return None
