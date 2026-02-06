# LocalBoost - Discover & Support Local Businesses

A stunning, modern web platform for discovering and supporting small, local businesses in your community. Built with a sleek Apple-inspired design, featuring 3D animations, smooth scroll effects, and comprehensive business discovery features.

![LocalBoost](https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200)

## Features

### Core Functionality
- **Smart Search & Browse** - Find businesses by category, name, or keywords
- **Category Filtering** - Browse Food, Retail, Services, Entertainment, and Health
- **Sorting Options** - Sort by rating, reviews, name, or newest
- **Ratings & Reviews** - Leave authentic reviews with CAPTCHA verification
- **Favorites/Bookmarks** - Save businesses you love for quick access
- **Deals & Coupons** - Access exclusive discounts and promotions
- **Custom Reports** - Generate detailed analytics with charts and export options
- **Interactive Help** - Smart Q&A assistant and comprehensive FAQ

### Technical Highlights
- **3D Intro Animation** - Stunning Three.js particle system and geometric shapes
- **2D Scroll Effects** - Smooth GSAP-powered animations and parallax
- **Responsive Design** - Works beautifully on desktop and mobile
- **Apple-Inspired UI** - Clean, minimal, sophisticated aesthetic
- **Bot Prevention** - CAPTCHA verification for authentic reviews
- **Real-time Charts** - Chart.js powered analytics visualization

## Tech Stack

### Backend
- **Python 3.x** - Core programming language
- **Flask** - Lightweight web framework
- **SQLite** - Database (via SQLAlchemy ORM)
- **SQLAlchemy** - Database ORM for data modeling

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS variables
- **JavaScript (ES6+)** - Interactive functionality
- **Three.js** - 3D graphics and animations
- **GSAP** - Animation library with ScrollTrigger
- **Chart.js** - Data visualization

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd localboost
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:5000`

## Project Structure

```
localboost/
├── app.py                 # Flask application & API routes
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates (Jinja2)
│   ├── index.html        # Landing page with 3D intro
│   ├── explore.html      # Business listing & search
│   ├── business_detail.html  # Individual business page
│   ├── deals.html        # Deals & coupons page
│   ├── favorites.html    # Saved businesses page
│   ├── reports.html      # Analytics & reports
│   └── help.html         # Help center & Q&A
├── static/               # Static assets (if needed)
│   ├── css/
│   ├── js/
│   └── images/
└── data/                 # Database storage
    └── localboost.db     # SQLite database (auto-created)
```

## Database Schema

### Tables

**Users**
- id, username, email, password_hash, created_at, is_verified

**Businesses**
- id, name, description, category, address, phone, email, website
- image_url, hours (JSON), latitude, longitude, created_at, is_verified

**Reviews**
- id, user_id, business_id, rating, title, content, created_at
- is_verified, helpful_count

**Deals**
- id, business_id, title, description, discount_type, discount_value
- code, start_date, end_date, terms, is_active, redemption_count

**Favorites**
- id, user_id, business_id, created_at, notes

**CaptchaChallenges**
- id, session_id, answer, created_at, is_solved

## API Endpoints

### Businesses
- `GET /api/businesses` - List businesses (with filtering & sorting)
- `GET /api/businesses/<id>` - Get business details
- `GET /api/categories` - Get all categories with counts

### Reviews
- `POST /api/reviews` - Create a review (requires CAPTCHA)

### Favorites
- `GET /api/favorites` - Get user's favorites
- `POST /api/favorites` - Add to favorites
- `DELETE /api/favorites/<id>` - Remove from favorites

### Deals
- `GET /api/deals` - Get all active deals

### Reports
- `POST /api/reports` - Generate custom report

### CAPTCHA
- `GET /api/captcha` - Get new CAPTCHA challenge
- `POST /api/captcha/verify` - Verify CAPTCHA answer

### Help
- `GET /api/help/search` - Search help topics

## Design Philosophy

LocalBoost follows Apple's design principles:
- **Clarity** - Text is legible, icons precise, minimal decoration
- **Deference** - Content is the focus, UI supports without competing
- **Depth** - Visual layers create hierarchy and understanding

### Color Palette
- Background: Deep blacks (#0a0a0a, #141414, #1f1f1f)
- Accent: Warm coral gradient (#ff6b35 → #f7931e)
- Text: White hierarchy (#ffffff, #a1a1a1, #6b6b6b)
- Borders: Subtle transparency (rgba(255,255,255,0.08))

## Credits

Built with passion for local businesses and community support.

### Libraries Used
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Three.js](https://threejs.org/) - 3D graphics
- [GSAP](https://greensock.com/gsap/) - Animation
- [Chart.js](https://www.chartjs.org/) - Charts
- [Inter Font](https://rsms.me/inter/) - Typography

### Image Credits
Sample images from [Unsplash](https://unsplash.com/)

## License

This project is for educational purposes. Feel free to use and modify.

---

Made with ❤️ for local communities
