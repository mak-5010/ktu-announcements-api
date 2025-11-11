# KTU Announcements API

A production-ready REST API that scrapes announcements from [KTU (Kerala Technological University)](https://ktu.edu.in/Menu/announcements) and serves them in a structured JSON format for easy integration with WordPress, mobile apps, or any other platform.

## Features

- **Automated Scraping**: Uses Selenium to scrape JavaScript-rendered content from KTU website
- **Smart Caching**: In-memory cache with automatic refresh every 30 minutes
- **Background Processing**: Non-blocking scraper runs in background threads
- **CORS Enabled**: Ready for cross-origin requests from WordPress
- **Production Ready**: Dockerized with health checks and proper error handling
- **Comprehensive Data**: Extracts titles, links, dates, messages, and attachments

## API Endpoints

### `GET /`
Welcome message with available endpoints

### `GET /api/ktu/announcements`
Get all announcements (cached data)

**Response:**
```json
{
  "fetched_at": "2025-11-12T00:00:00Z",
  "count": 10,
  "cache_age_seconds": 120,
  "cached_at": "2025-11-12T00:00:00",
  "announcements": [
    {
      "title": "Announcement Title",
      "link": "https://ktu.edu.in/...",
      "date": "12/11/2025",
      "message_text": "Full announcement text",
      "message_html": "<p>HTML content</p>",
      "attachments": [
        {
          "title": "Document Name",
          "href": "https://ktu.edu.in/path/to/file.pdf"
        }
      ]
    }
  ]
}
```

### `GET /api/ktu/refresh`
Force refresh - triggers immediate scraping

**Response:**
```json
{
  "message": "Scraper started",
  "status": "running",
  "estimated_time": "30-60 seconds"
}
```

### `GET /api/ktu/status`
Get cache and scraper status

**Response:**
```json
{
  "is_scraping": false,
  "has_data": true,
  "last_updated": "2025-11-12T00:00:00",
  "cache_age_seconds": 120,
  "announcement_count": 10
}
```

### `GET /health`
Health check endpoint (for monitoring)

## Local Development

### Prerequisites
- Python 3.11+
- Chrome/Chromium browser

### Setup

1. Clone the repository:
```bash
git clone https://github.com/mak-5010/ktu-announcements-api.git
cd ktu-announcements-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python server.py
```

The API will be available at `http://localhost:8080`

### Test the scraper directly:
```bash
python ktu_scrape_site.py
```

This creates `ktu_announcements.json` with scraped data.

## Deployment on Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Blueprint"
4. Connect your repository
5. Render will automatically detect `render.yaml` and deploy

### Option 2: Manual Docker Deployment

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: ktu-announcements-api
   - **Runtime**: Docker
   - **Region**: Singapore (or closest to your users)
   - **Plan**: Starter ($7/month) or Free
   - **Health Check Path**: `/health`

5. Click "Create Web Service"

### Environment Variables (Optional)

You can set these in Render dashboard:
- `PORT`: 8080 (default)
- `HEADLESS`: true (default)

## WordPress Integration

### Sample WordPress Plugin Structure

Create a WordPress plugin to fetch and display announcements:

```php
<?php
/**
 * Plugin Name: KTU Announcements
 * Description: Fetches and displays KTU announcements
 * Version: 1.0
 */

// Fetch announcements
function ktu_fetch_announcements() {
    $api_url = 'https://your-render-app.onrender.com/api/ktu/announcements';

    $response = wp_remote_get($api_url, array('timeout' => 30));

    if (is_wp_error($response)) {
        return array();
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    return $data['announcements'] ?? array();
}

// Shortcode: [ktu_announcements]
function ktu_announcements_shortcode($atts) {
    $atts = shortcode_atts(array(
        'limit' => 10
    ), $atts);

    $announcements = ktu_fetch_announcements();
    $announcements = array_slice($announcements, 0, $atts['limit']);

    ob_start();
    ?>
    <div class="ktu-announcements">
        <?php foreach ($announcements as $item): ?>
            <div class="ktu-announcement-item">
                <h3>
                    <a href="<?php echo esc_url($item['link']); ?>" target="_blank">
                        <?php echo esc_html($item['title']); ?>
                    </a>
                </h3>
                <p class="ktu-date"><?php echo esc_html($item['date']); ?></p>
                <div class="ktu-message">
                    <?php echo wp_kses_post($item['message_html']); ?>
                </div>
                <?php if (!empty($item['attachments'])): ?>
                    <div class="ktu-attachments">
                        <strong>Attachments:</strong>
                        <?php foreach ($item['attachments'] as $att): ?>
                            <a href="<?php echo esc_url($att['href']); ?>" target="_blank">
                                <?php echo esc_html($att['title']); ?>
                            </a>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>
        <?php endforeach; ?>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('ktu_announcements', 'ktu_announcements_shortcode');
```

### Elementor Widget

For Elementor integration, you can:
1. Use the shortcode `[ktu_announcements limit="5"]` in Elementor's Shortcode widget
2. Create a custom Elementor widget that calls `ktu_fetch_announcements()`
3. Use Elementor's Dynamic Tags to inject announcement data

## Architecture

### How It Works

1. **On Startup**:
   - Loads existing JSON file into cache (if available)
   - Starts background scraper if no data exists
   - Initializes scheduler for periodic updates

2. **Background Scheduler**:
   - Runs scraper every 30 minutes
   - Uses thread-safe locks to prevent concurrent scraping
   - Updates cache when scraping completes

3. **API Requests**:
   - Serves data instantly from in-memory cache
   - Auto-refreshes if cache is older than 1 hour
   - No blocking - scraper runs in background

4. **Scraping Process**:
   - Uses Selenium with headless Chrome
   - Waits for JavaScript-rendered content
   - Extracts structured data with multiple fallbacks
   - Handles errors gracefully

### Performance

- **Response Time**: < 100ms (cached)
- **Scraping Time**: 30-60 seconds (background)
- **Cache Duration**: 1 hour (configurable)
- **Auto-refresh**: Every 30 minutes

## Security Improvements

- Replaced `os.system()` with `subprocess.run()` to prevent command injection
- Added timeout limits to prevent hanging processes
- Thread-safe cache operations with locks
- Comprehensive error handling
- CORS enabled only for API endpoints

## Monitoring

### Health Checks
```bash
curl https://your-render-app.onrender.com/health
```

### Check Status
```bash
curl https://your-render-app.onrender.com/api/ktu/status
```

### View Logs
In Render dashboard → Your Service → Logs

## Troubleshooting

### Issue: Scraper timeout
**Solution**: Increase `WAIT_SECONDS` in `ktu_scrape_site.py`

### Issue: Chrome not found
**Solution**: Ensure Dockerfile installs Chrome properly (already configured)

### Issue: Memory issues on free tier
**Solution**: Upgrade to Starter plan or reduce scraping frequency

### Issue: CORS errors from WordPress
**Solution**: CORS is already enabled via flask-cors

## Cost Estimate

### Render Pricing
- **Free Tier**: Limited to 750 hours/month, spins down after inactivity
- **Starter**: $7/month, always running, better for production
- **Recommended**: Starter plan for reliable WordPress integration

## Support

For issues or questions:
1. Check [KTU Website](https://ktu.edu.in/Menu/announcements) to verify it's accessible
2. Review Render logs for errors
3. Test locally first before deploying

## License

MIT License - Feel free to modify and use for your needs

## Contributing

Pull requests welcome! Please test locally before submitting.
