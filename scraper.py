#!/usr/bin/env python3
"""
WFMU Give The Drummer Some Podcast Generator
Scrapes the WFMU playlist page and generates an RSS feed
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import re

def scrape_wfmu_page():
    """Scrape the WFMU playlist page for episode data"""
    url = "https://wfmu.org/playlists/ds"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    episodes = []

    # Look for playlist entries in table rows
    for row in soup.find_all('tr'):
        try:
            cells = row.find_all('td')
            if len(cells) < 3:
                continue

            # Check if this looks like a playlist row
            date_cell = cells[0]
            title_cell = None
            mp3_cell = None

            # Find cells with links
            for cell in cells:
                if cell.find('a'):
                    link = cell.find('a')
                    href = link.get('href', '')
                    if 'playlist' in href:
                        title_cell = cell
                    elif '.mp3' in href or 'archive' in href:
                        mp3_cell = cell

            if not title_cell:
                continue

            # Extract date
            date_text = date_cell.get_text(strip=True)
            if not re.match(r'\d+/\d+/\d+', date_text):
                continue

            # Extract title and playlist URL
            title_link = title_cell.find('a')
            title = title_link.get_text(strip=True)
            playlist_url = title_link.get('href')
            if playlist_url and not playlist_url.startswith('http'):
                playlist_url = f"https://wfmu.org{playlist_url}"

            # Extract MP3 URL
            mp3_url = None
            if mp3_cell:
                mp3_link = mp3_cell.find('a')
                if mp3_link:
                    mp3_url = mp3_link.get('href')
                    if mp3_url and not mp3_url.startswith('http'):
                        mp3_url = f"https://wfmu.org{mp3_url}"

            episode = {
                'date': date_text,
                'title': title,
                'playlist_url': playlist_url,
                'mp3_url': mp3_url
            }
            episodes.append(episode)

        except Exception as e:
            print(f"Error parsing row: {e}")
            continue

    return episodes

def parse_date(date_str):
    """Parse date string in MM/DD/YY or MM/DD/YYYY format"""
    try:
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                month, day, year = parts
                if len(year) == 2:
                    year = f"20{year}"
                return datetime(int(year), int(month), int(day), 9, 0)  # 9 AM show time
    except:
        pass
    return datetime.now()

def generate_rss_feed(episodes):
    """Generate RSS feed from episode data"""

    # Create RSS root with proper namespaces
    rss = ET.Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
    rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')

    channel = ET.SubElement(rss, 'channel')

    # Channel metadata
    ET.SubElement(channel, 'title').text = 'Give The Drummer Some - WFMU'
    ET.SubElement(channel, 'description').text = 'Doug Schulkind\'s eclectic radio show from WFMU featuring Micronesian doo-wop, Appalachian mambo, and more. Fridays 9am-Noon EST.'
    ET.SubElement(channel, 'link').text = 'https://wfmu.org/playlists/ds'
    ET.SubElement(channel, 'language').text = 'en-us'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    ET.SubElement(channel, 'generator').text = 'WFMU Podcast Generator'

    # iTunes specific tags
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = 'Doug Schulkind / WFMU'
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}summary').text = 'Eclectic music show from WFMU'
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category', text='Music')

    # Sort episodes by date (newest first)
    episodes_sorted = sorted(episodes, key=lambda x: parse_date(x['date']), reverse=True)

    # Add episodes
    for episode in episodes_sorted:
        item = ET.SubElement(channel, 'item')

        title_text = f"Give The Drummer Some - {episode['date']}"
        if episode['title']:
            title_text += f": {episode['title']}"

        ET.SubElement(item, 'title').text = title_text

        description = f"Give The Drummer Some from {episode['date']}"
        if episode['title']:
            description += f" - {episode['title']}"
        if episode['playlist_url']:
            description += f"\n\nView playlist: {episode['playlist_url']}"

        ET.SubElement(item, 'description').text = description
        ET.SubElement(item, 'link').text = episode['playlist_url'] or 'https://wfmu.org/playlists/ds'

        # Use playlist URL as GUID if no MP3
        guid_url = episode['mp3_url'] or episode['playlist_url'] or f"https://wfmu.org/playlists/ds#{episode['date']}"
        ET.SubElement(item, 'guid').text = guid_url

        # Add audio enclosure if MP3 exists
        if episode['mp3_url']:
            enclosure = ET.SubElement(item, 'enclosure')
            enclosure.set('url', episode['mp3_url'])
            enclosure.set('type', 'audio/mpeg')
            enclosure.set('length', '0')  # Unknown file size

        # Parse and format date
        parsed_date = parse_date(episode['date'])
        ET.SubElement(item, 'pubDate').text = parsed_date.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return ET.tostring(rss, encoding='unicode')

def format_xml(xml_string):
    """Add proper XML formatting with DOCTYPE"""
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    return header + xml_string

def main():
    """Main function to scrape and generate RSS"""
    print("Scraping WFMU playlist page...")
    episodes = scrape_wfmu_page()

    if not episodes:
        print("No episodes found!")
        return

    print(f"Found {len(episodes)} episodes")

    print("Generating RSS feed...")
    rss_content = generate_rss_feed(episodes)
    formatted_xml = format_xml(rss_content)

    # Save RSS feed
    with open('podcast.xml', 'w', encoding='utf-8') as f:
        f.write(formatted_xml)

    print("RSS feed saved as 'podcast.xml'")
    print(f"Feed contains {len([e for e in episodes if e.get('mp3_url')])} episodes with audio")

if __name__ == '__main__':
    main()