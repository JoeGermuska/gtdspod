# WFMU Give The Drummer Some Podcast Feed

Automatically converts the [WFMU Give The Drummer Some playlist page](https://wfmu.org/playlists/ds) into a podcast feed that updates daily.

## Setup Instructions

1. **Fork/clone this repository** to your GitHub account

2. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Set Source to "GitHub Actions"

3. **Enable GitHub Actions**:
   - Go to repository Actions tab
   - Enable workflows if prompted

4. **Run initial generation**:
   - Go to Actions → "Update WFMU Podcast Feed"
   - Click "Run workflow" → "Run workflow"

5. **Get your RSS URL**:
   - After the action completes, your feed will be available at:
   - `https://[your-username].github.io/[repository-name]/podcast.xml`

6. **Add to Overcast**:
   - Open Overcast
   - Add podcast by URL
   - Paste your RSS URL

## How it works

- GitHub Actions runs daily at 2 PM EST
- Scrapes the WFMU playlist page for new episodes
- Generates an RSS feed with audio links
- Publishes via GitHub Pages
- Your podcast app automatically gets updates

The feed includes episodes with MP3 audio links and playlist information.