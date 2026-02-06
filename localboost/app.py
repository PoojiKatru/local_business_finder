"""
LocalBoost - Discover & Support Local Businesses
A sleek, modern platform for finding and supporting small businesses in your community.

Tech Stack:
- Backend: Python Flask
- Database: SQLite with SQLAlchemy
- Frontend: HTML5, CSS3, JavaScript
- 3D Graphics: Three.js
- Animations: GSAP, ScrollTrigger
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string
import hashlib
import json
import os

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'localboost_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///localboost.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# ============================================
# DATABASE MODELS
# ============================================

class User(db.Model):
    """User model for authentication and tracking"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)

    # Relationships
    reviews = db.relationship('Review', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    def set_password(self, password):
        """Hash and set the user password"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        """Verify password against stored hash"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


class Business(db.Model):
    """Business model representing local businesses"""
    __tablename__ = 'businesses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # food, retail, services, entertainment, health
    address = db.Column(db.String(300), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    hours = db.Column(db.Text)  # JSON string of operating hours
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=True)

    # Relationships
    reviews = db.relationship('Review', backref='business', lazy=True)
    deals = db.relationship('Deal', backref='business', lazy=True)
    favorites = db.relationship('Favorite', backref='business', lazy=True)

    @property
    def average_rating(self):
        """Calculate average rating from all reviews"""
        if not self.reviews:
            return 0
        return sum(r.rating for r in self.reviews) / len(self.reviews)

    @property
    def review_count(self):
        """Get total number of reviews"""
        return len(self.reviews)


class Review(db.Model):
    """Review model for business ratings and feedback"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=True)
    helpful_count = db.Column(db.Integer, default=0)


class Deal(db.Model):
    """Deal/Coupon model for special offers"""
    __tablename__ = 'deals'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    discount_type = db.Column(db.String(20))  # percentage, fixed, bogo
    discount_value = db.Column(db.Float)
    code = db.Column(db.String(50))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    terms = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    redemption_count = db.Column(db.Integer, default=0)


class Favorite(db.Model):
    """Favorite/Bookmark model for saved businesses"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # Personal notes about the business


class CaptchaChallenge(db.Model):
    """CAPTCHA challenge for bot prevention"""
    __tablename__ = 'captcha_challenges'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_solved = db.Column(db.Boolean, default=False)


# ============================================
# CAPTCHA GENERATION
# ============================================

def generate_math_captcha():
    """Generate a simple math CAPTCHA challenge"""
    operations = [
        ('+', lambda a, b: a + b),
        ('-', lambda a, b: a - b),
        ('×', lambda a, b: a * b)
    ]

    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)

    # Ensure subtraction doesn't go negative
    if num1 < num2:
        num1, num2 = num2, num1

    op_symbol, op_func = random.choice(operations)
    answer = op_func(num1, num2)

    question = f"What is {num1} {op_symbol} {num2}?"
    return question, str(answer)


# ============================================
# ROUTES - Pages
# ============================================

@app.route('/')
def index():
    """Main landing page with 3D intro"""
    return render_template('index.html')


@app.route('/explore')
def explore():
    """Business exploration page"""
    return render_template('explore.html')


@app.route('/business/<int:business_id>')
def business_detail(business_id):
    """Individual business detail page"""
    business = Business.query.get_or_404(business_id)
    return render_template('business_detail.html', business=business)


@app.route('/favorites')
def favorites_page():
    """User's saved businesses page"""
    return render_template('favorites.html')


@app.route('/deals')
def deals_page():
    """Active deals and coupons page"""
    return render_template('deals.html')


@app.route('/reports')
def reports_page():
    """Customizable reports page"""
    return render_template('reports.html')


@app.route('/help')
def help_page():
    """Interactive help and Q&A page"""
    return render_template('help.html')


# ============================================
# ROUTES - API Endpoints
# ============================================

@app.route('/api/businesses', methods=['GET'])
def get_businesses():
    """
    Get businesses with filtering and sorting options

    Query Parameters:
    - category: Filter by category (food, retail, services, etc.)
    - sort: Sort by (rating, reviews, name, newest)
    - search: Search term for name/description
    - limit: Number of results (default 20)
    - offset: Pagination offset
    """
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'rating')
    search = request.args.get('search', '')
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))

    # Base query
    query = Business.query

    # Apply category filter
    if category and category != 'all':
        query = query.filter(Business.category == category)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Business.name.ilike(search_term),
                Business.description.ilike(search_term)
            )
        )

    # Get all matching businesses
    businesses = query.all()

    # Sort in Python to handle computed properties
    if sort_by == 'rating':
        businesses.sort(key=lambda b: b.average_rating, reverse=True)
    elif sort_by == 'reviews':
        businesses.sort(key=lambda b: b.review_count, reverse=True)
    elif sort_by == 'name':
        businesses.sort(key=lambda b: b.name.lower())
    elif sort_by == 'newest':
        businesses.sort(key=lambda b: b.created_at, reverse=True)

    # Apply pagination
    paginated = businesses[offset:offset + limit]

    # Serialize results
    result = []
    for business in paginated:
        result.append({
            'id': business.id,
            'name': business.name,
            'description': business.description,
            'category': business.category,
            'address': business.address,
            'phone': business.phone,
            'email': business.email,
            'website': business.website,
            'image_url': business.image_url,
            'hours': json.loads(business.hours) if business.hours else None,
            'average_rating': round(business.average_rating, 1),
            'review_count': business.review_count,
            'is_verified': business.is_verified,
            'has_deals': len([d for d in business.deals if d.is_active]) > 0
        })

    return jsonify({
        'businesses': result,
        'total': len(businesses),
        'limit': limit,
        'offset': offset
    })


@app.route('/api/businesses/<int:business_id>', methods=['GET'])
def get_business(business_id):
    """Get detailed information for a single business"""
    business = Business.query.get_or_404(business_id)

    # Get active deals
    active_deals = [
        {
            'id': d.id,
            'title': d.title,
            'description': d.description,
            'discount_type': d.discount_type,
            'discount_value': d.discount_value,
            'code': d.code,
            'end_date': d.end_date.isoformat() if d.end_date else None,
            'terms': d.terms
        }
        for d in business.deals if d.is_active
    ]

    # Get reviews
    reviews = [
        {
            'id': r.id,
            'user': r.user.username,
            'rating': r.rating,
            'title': r.title,
            'content': r.content,
            'created_at': r.created_at.isoformat(),
            'helpful_count': r.helpful_count
        }
        for r in sorted(business.reviews, key=lambda x: x.created_at, reverse=True)
    ]

    return jsonify({
        'id': business.id,
        'name': business.name,
        'description': business.description,
        'category': business.category,
        'address': business.address,
        'phone': business.phone,
        'email': business.email,
        'website': business.website,
        'image_url': business.image_url,
        'hours': json.loads(business.hours) if business.hours else None,
        'latitude': business.latitude,
        'longitude': business.longitude,
        'average_rating': round(business.average_rating, 1),
        'review_count': business.review_count,
        'is_verified': business.is_verified,
        'deals': active_deals,
        'reviews': reviews
    })


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all business categories with counts"""
    categories = db.session.query(
        Business.category,
        db.func.count(Business.id).label('count')
    ).group_by(Business.category).all()

    return jsonify([
        {'name': cat, 'count': count}
        for cat, count in categories
    ])


@app.route('/api/captcha', methods=['GET'])
def get_captcha():
    """Generate a new CAPTCHA challenge"""
    question, answer = generate_math_captcha()

    # Create session ID if not exists
    if 'captcha_session' not in session:
        session['captcha_session'] = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    # Store challenge in database
    challenge = CaptchaChallenge(
        session_id=session['captcha_session'],
        answer=answer
    )
    db.session.add(challenge)
    db.session.commit()

    return jsonify({
        'challenge_id': challenge.id,
        'question': question
    })


@app.route('/api/captcha/verify', methods=['POST'])
def verify_captcha():
    """Verify CAPTCHA answer"""
    data = request.get_json()
    challenge_id = data.get('challenge_id')
    user_answer = data.get('answer', '').strip()

    challenge = CaptchaChallenge.query.get(challenge_id)

    if not challenge:
        return jsonify({'success': False, 'error': 'Invalid challenge'}), 400

    # Check if challenge is expired (5 minutes)
    if datetime.utcnow() - challenge.created_at > timedelta(minutes=5):
        return jsonify({'success': False, 'error': 'Challenge expired'}), 400

    if challenge.answer == user_answer:
        challenge.is_solved = True
        db.session.commit()
        session['captcha_verified'] = True
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Incorrect answer'}), 400


@app.route('/api/reviews', methods=['POST'])
def create_review():
    """Create a new review (requires CAPTCHA verification)"""
    # Check CAPTCHA verification
    if not session.get('captcha_verified'):
        return jsonify({'error': 'Please complete CAPTCHA verification'}), 403

    data = request.get_json()

    # Validate input
    business_id = data.get('business_id')
    rating = data.get('rating')
    title = data.get('title', '')
    content = data.get('content', '')

    if not all([business_id, rating, content]):
        return jsonify({'error': 'Missing required fields'}), 400

    if not 1 <= int(rating) <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    if len(content) < 10:
        return jsonify({'error': 'Review must be at least 10 characters'}), 400

    # Get or create anonymous user for demo
    user = User.query.filter_by(username='guest').first()
    if not user:
        user = User(username='guest', email='guest@localboost.com', password_hash='guest')
        db.session.add(user)
        db.session.commit()

    # Create review
    review = Review(
        user_id=user.id,
        business_id=business_id,
        rating=int(rating),
        title=title,
        content=content
    )
    db.session.add(review)
    db.session.commit()

    # Reset CAPTCHA verification
    session['captcha_verified'] = False

    return jsonify({
        'success': True,
        'review': {
            'id': review.id,
            'rating': review.rating,
            'title': review.title,
            'content': review.content,
            'created_at': review.created_at.isoformat()
        }
    })


@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """Get user's favorite businesses"""
    # For demo, use guest user
    user = User.query.filter_by(username='guest').first()
    if not user:
        return jsonify({'favorites': []})

    favorites = []
    for fav in user.favorites:
        business = fav.business
        favorites.append({
            'id': fav.id,
            'business_id': business.id,
            'business_name': business.name,
            'business_category': business.category,
            'business_image': business.image_url,
            'business_rating': round(business.average_rating, 1),
            'notes': fav.notes,
            'created_at': fav.created_at.isoformat()
        })

    return jsonify({'favorites': favorites})


@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """Add a business to favorites"""
    data = request.get_json()
    business_id = data.get('business_id')
    notes = data.get('notes', '')

    if not business_id:
        return jsonify({'error': 'Business ID required'}), 400

    # Get or create guest user
    user = User.query.filter_by(username='guest').first()
    if not user:
        user = User(username='guest', email='guest@localboost.com', password_hash='guest')
        db.session.add(user)
        db.session.commit()

    # Check if already favorited
    existing = Favorite.query.filter_by(user_id=user.id, business_id=business_id).first()
    if existing:
        return jsonify({'error': 'Already in favorites'}), 400

    favorite = Favorite(user_id=user.id, business_id=business_id, notes=notes)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({'success': True, 'favorite_id': favorite.id})


@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def remove_favorite(favorite_id):
    """Remove a business from favorites"""
    favorite = Favorite.query.get_or_404(favorite_id)
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'success': True})


@app.route('/api/deals', methods=['GET'])
def get_deals():
    """Get all active deals"""
    category = request.args.get('category', '')

    query = Deal.query.filter(Deal.is_active == True)

    if category and category != 'all':
        query = query.join(Business).filter(Business.category == category)

    deals = query.all()

    result = []
    for deal in deals:
        result.append({
            'id': deal.id,
            'business_id': deal.business.id,
            'business_name': deal.business.name,
            'business_category': deal.business.category,
            'business_image': deal.business.image_url,
            'title': deal.title,
            'description': deal.description,
            'discount_type': deal.discount_type,
            'discount_value': deal.discount_value,
            'code': deal.code,
            'end_date': deal.end_date.isoformat() if deal.end_date else None,
            'terms': deal.terms
        })

    return jsonify({'deals': result})


@app.route('/api/reports', methods=['POST'])
def generate_report():
    """Generate a customizable report"""
    data = request.get_json()

    report_type = data.get('type', 'summary')  # summary, category, ratings, deals
    category_filter = data.get('category', 'all')
    date_range = data.get('date_range', 'all')  # all, week, month, year
    include_reviews = data.get('include_reviews', True)
    include_deals = data.get('include_deals', True)

    # Base query
    query = Business.query

    if category_filter and category_filter != 'all':
        query = query.filter(Business.category == category_filter)

    businesses = query.all()

    # Calculate statistics
    total_businesses = len(businesses)
    total_reviews = sum(b.review_count for b in businesses)
    avg_rating = sum(b.average_rating for b in businesses) / total_businesses if total_businesses > 0 else 0

    # Category breakdown
    category_stats = {}
    for business in businesses:
        cat = business.category
        if cat not in category_stats:
            category_stats[cat] = {'count': 0, 'total_rating': 0, 'reviews': 0}
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_rating'] += business.average_rating
        category_stats[cat]['reviews'] += business.review_count

    for cat in category_stats:
        stats = category_stats[cat]
        stats['avg_rating'] = round(stats['total_rating'] / stats['count'], 1) if stats['count'] > 0 else 0

    # Top rated businesses
    top_rated = sorted(businesses, key=lambda b: b.average_rating, reverse=True)[:10]

    # Most reviewed
    most_reviewed = sorted(businesses, key=lambda b: b.review_count, reverse=True)[:10]

    # Active deals count
    active_deals = Deal.query.filter(Deal.is_active == True).count()

    report = {
        'generated_at': datetime.utcnow().isoformat(),
        'filters': {
            'category': category_filter,
            'date_range': date_range
        },
        'summary': {
            'total_businesses': total_businesses,
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'active_deals': active_deals
        },
        'category_breakdown': category_stats,
        'top_rated': [
            {
                'id': b.id,
                'name': b.name,
                'category': b.category,
                'rating': round(b.average_rating, 1),
                'reviews': b.review_count
            }
            for b in top_rated
        ],
        'most_reviewed': [
            {
                'id': b.id,
                'name': b.name,
                'category': b.category,
                'rating': round(b.average_rating, 1),
                'reviews': b.review_count
            }
            for b in most_reviewed
        ]
    }

    return jsonify(report)


@app.route('/api/help/search', methods=['GET'])
def search_help():
    """Search help topics"""
    query = request.args.get('q', '').lower()

    # Help topics database
    help_topics = [
        {
            'id': 1,
            'title': 'How to find businesses',
            'content': 'Use the search bar or browse by category to discover local businesses. You can filter by food, retail, services, entertainment, and health categories.',
            'keywords': ['find', 'search', 'discover', 'browse', 'category']
        },
        {
            'id': 2,
            'title': 'How to leave a review',
            'content': 'Navigate to a business page and scroll to the reviews section. Complete the CAPTCHA verification, then fill out the rating and review form. Reviews help other community members make informed decisions.',
            'keywords': ['review', 'rating', 'feedback', 'stars', 'comment']
        },
        {
            'id': 3,
            'title': 'Saving favorite businesses',
            'content': 'Click the heart icon on any business card or detail page to save it to your favorites. Access your saved businesses anytime from the Favorites page.',
            'keywords': ['favorite', 'bookmark', 'save', 'heart', 'list']
        },
        {
            'id': 4,
            'title': 'Finding deals and coupons',
            'content': 'Visit the Deals page to see all active promotions. You can filter by category and view discount codes, expiration dates, and terms.',
            'keywords': ['deal', 'coupon', 'discount', 'promotion', 'offer', 'save']
        },
        {
            'id': 5,
            'title': 'Generating reports',
            'content': 'The Reports page allows you to create customized analytics. Filter by category, date range, and choose what data to include. Export your reports for further analysis.',
            'keywords': ['report', 'analytics', 'data', 'statistics', 'export', 'analysis']
        },
        {
            'id': 6,
            'title': 'Understanding ratings',
            'content': 'Businesses are rated on a 1-5 star scale. The displayed rating is an average of all user reviews. Higher ratings indicate better customer satisfaction.',
            'keywords': ['rating', 'stars', 'score', 'average', 'quality']
        },
        {
            'id': 7,
            'title': 'CAPTCHA verification',
            'content': 'We use CAPTCHA challenges to prevent automated bot activity and ensure genuine reviews. Simply solve the math problem to verify you are human.',
            'keywords': ['captcha', 'verification', 'bot', 'security', 'human']
        },
        {
            'id': 8,
            'title': 'Business categories explained',
            'content': 'Food: restaurants, cafes, bakeries. Retail: shops, boutiques, stores. Services: salons, repairs, professional services. Entertainment: venues, activities. Health: wellness, fitness, medical.',
            'keywords': ['category', 'type', 'food', 'retail', 'services', 'entertainment', 'health']
        }
    ]

    if not query:
        return jsonify({'topics': help_topics})

    # Search and rank results
    results = []
    for topic in help_topics:
        score = 0
        if query in topic['title'].lower():
            score += 10
        if query in topic['content'].lower():
            score += 5
        for keyword in topic['keywords']:
            if query in keyword or keyword in query:
                score += 3

        if score > 0:
            results.append({**topic, 'relevance': score})

    results.sort(key=lambda x: x['relevance'], reverse=True)

    return jsonify({'topics': results})


# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_sample_data():
    """Initialize database with sample data"""

    # Sample businesses
    businesses_data = [
        {
            'name': 'The Rustic Table',
            'description': 'Farm-to-table restaurant featuring locally sourced ingredients and seasonal menus. Our chefs create memorable dining experiences with fresh, organic produce from nearby farms.',
            'category': 'food',
            'address': '123 Main Street, Downtown',
            'phone': '(555) 123-4567',
            'email': 'hello@rustictable.com',
            'website': 'https://rustictable.com',
            'image_url': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
            'hours': '{"mon": "11:00-21:00", "tue": "11:00-21:00", "wed": "11:00-21:00", "thu": "11:00-22:00", "fri": "11:00-23:00", "sat": "10:00-23:00", "sun": "10:00-20:00"}'
        },
        {
            'name': 'Craft & Co',
            'description': 'Artisan goods and handcrafted items from local makers. Discover unique gifts, home decor, and accessories that tell a story.',
            'category': 'retail',
            'address': '456 Oak Avenue, Arts District',
            'phone': '(555) 234-5678',
            'email': 'shop@craftandco.com',
            'website': 'https://craftandco.com',
            'image_url': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800',
            'hours': '{"mon": "10:00-18:00", "tue": "10:00-18:00", "wed": "10:00-18:00", "thu": "10:00-20:00", "fri": "10:00-20:00", "sat": "09:00-20:00", "sun": "11:00-17:00"}'
        },
        {
            'name': 'Bloom Beauty Studio',
            'description': 'Full-service beauty salon offering haircuts, coloring, skincare, and spa treatments. Our experienced stylists help you look and feel your best.',
            'category': 'services',
            'address': '789 Elm Street, Midtown',
            'phone': '(555) 345-6789',
            'email': 'book@bloombeauty.com',
            'website': 'https://bloombeauty.com',
            'image_url': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800',
            'hours': '{"mon": "closed", "tue": "09:00-19:00", "wed": "09:00-19:00", "thu": "09:00-20:00", "fri": "09:00-20:00", "sat": "08:00-18:00", "sun": "10:00-16:00"}'
        },
        {
            'name': 'Pixel Arcade & Gaming',
            'description': 'Retro arcade meets modern gaming lounge. Play classic pinball machines, vintage video games, and the latest VR experiences.',
            'category': 'entertainment',
            'address': '321 Game Lane, Entertainment District',
            'phone': '(555) 456-7890',
            'email': 'play@pixelarcade.com',
            'website': 'https://pixelarcade.com',
            'image_url': 'https://images.unsplash.com/photo-1511882150382-421056c89033?w=800',
            'hours': '{"mon": "14:00-23:00", "tue": "14:00-23:00", "wed": "14:00-23:00", "thu": "14:00-24:00", "fri": "12:00-02:00", "sat": "10:00-02:00", "sun": "10:00-22:00"}'
        },
        {
            'name': 'Zenith Yoga & Wellness',
            'description': 'Find your balance at our tranquil yoga studio. We offer classes for all levels, meditation sessions, and holistic wellness programs.',
            'category': 'health',
            'address': '567 Peaceful Way, Wellness Center',
            'phone': '(555) 567-8901',
            'email': 'namaste@zenithyoga.com',
            'website': 'https://zenithyoga.com',
            'image_url': 'https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=800',
            'hours': '{"mon": "06:00-21:00", "tue": "06:00-21:00", "wed": "06:00-21:00", "thu": "06:00-21:00", "fri": "06:00-20:00", "sat": "07:00-18:00", "sun": "08:00-16:00"}'
        },
        {
            'name': 'The Daily Grind',
            'description': 'Specialty coffee roastery and cafe. We source beans ethically and roast in-house. Enjoy expertly crafted espresso drinks and fresh pastries.',
            'category': 'food',
            'address': '890 Coffee Court, Riverside',
            'phone': '(555) 678-9012',
            'email': 'brew@dailygrind.com',
            'website': 'https://dailygrind.com',
            'image_url': 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800',
            'hours': '{"mon": "06:00-18:00", "tue": "06:00-18:00", "wed": "06:00-18:00", "thu": "06:00-18:00", "fri": "06:00-19:00", "sat": "07:00-19:00", "sun": "07:00-17:00"}'
        },
        {
            'name': 'Green Thumb Garden Center',
            'description': 'Everything for your garden and outdoor space. Plants, tools, soil, and expert advice from our passionate horticulturists.',
            'category': 'retail',
            'address': '234 Botanical Blvd, Garden District',
            'phone': '(555) 789-0123',
            'email': 'grow@greenthumb.com',
            'website': 'https://greenthumb.com',
            'image_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800',
            'hours': '{"mon": "08:00-18:00", "tue": "08:00-18:00", "wed": "08:00-18:00", "thu": "08:00-18:00", "fri": "08:00-18:00", "sat": "07:00-19:00", "sun": "09:00-17:00"}'
        },
        {
            'name': 'Fix-It Tech Solutions',
            'description': 'Computer repair, phone screen replacement, and IT support for homes and small businesses. Fast, reliable, and affordable.',
            'category': 'services',
            'address': '456 Tech Plaza, Innovation Hub',
            'phone': '(555) 890-1234',
            'email': 'help@fixittech.com',
            'website': 'https://fixittech.com',
            'image_url': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800',
            'hours': '{"mon": "09:00-18:00", "tue": "09:00-18:00", "wed": "09:00-18:00", "thu": "09:00-18:00", "fri": "09:00-17:00", "sat": "10:00-16:00", "sun": "closed"}'
        },
        {
            'name': 'Moonlight Cinema',
            'description': 'Indie film theater showcasing independent and international cinema. Comfortable seating, craft beer, and gourmet snacks.',
            'category': 'entertainment',
            'address': '789 Film Row, Cultural Center',
            'phone': '(555) 901-2345',
            'email': 'tickets@moonlightcinema.com',
            'website': 'https://moonlightcinema.com',
            'image_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800',
            'hours': '{"mon": "16:00-23:00", "tue": "16:00-23:00", "wed": "16:00-23:00", "thu": "16:00-23:00", "fri": "14:00-24:00", "sat": "12:00-24:00", "sun": "12:00-22:00"}'
        },
        {
            'name': 'Peak Performance Gym',
            'description': 'State-of-the-art fitness facility with personal training, group classes, and top-tier equipment. Achieve your fitness goals with us.',
            'category': 'health',
            'address': '901 Fitness Lane, Sports Complex',
            'phone': '(555) 012-3456',
            'email': 'join@peakgym.com',
            'website': 'https://peakgym.com',
            'image_url': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800',
            'hours': '{"mon": "05:00-23:00", "tue": "05:00-23:00", "wed": "05:00-23:00", "thu": "05:00-23:00", "fri": "05:00-22:00", "sat": "06:00-20:00", "sun": "07:00-18:00"}'
        },
        {
            'name': 'Bella Italia Trattoria',
            'description': 'Authentic Italian cuisine made with imported ingredients and family recipes. Wood-fired pizzas, handmade pasta, and fine wines.',
            'category': 'food',
            'address': '345 Italian Way, Little Italy',
            'phone': '(555) 234-5670',
            'email': 'ciao@bellaitalia.com',
            'website': 'https://bellaitalia.com',
            'image_url': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800',
            'hours': '{"mon": "closed", "tue": "17:00-22:00", "wed": "17:00-22:00", "thu": "17:00-22:00", "fri": "17:00-23:00", "sat": "12:00-23:00", "sun": "12:00-21:00"}'
        },
        {
            'name': 'Page Turner Books',
            'description': 'Independent bookstore with curated selections, author events, and a cozy reading nook. Supporting literacy in our community.',
            'category': 'retail',
            'address': '678 Literary Lane, University District',
            'phone': '(555) 345-6780',
            'email': 'read@pageturner.com',
            'website': 'https://pageturner.com',
            'image_url': 'https://images.unsplash.com/photo-1526243741027-444d633d7365?w=800',
            'hours': '{"mon": "09:00-20:00", "tue": "09:00-20:00", "wed": "09:00-20:00", "thu": "09:00-21:00", "fri": "09:00-21:00", "sat": "09:00-21:00", "sun": "10:00-18:00"}'
        }
    ]

    # Create businesses
    for data in businesses_data:
        business = Business(**data)
        db.session.add(business)

    db.session.commit()

    # Create guest user
    guest = User(username='guest', email='guest@localboost.com')
    guest.set_password('guest123')
    db.session.add(guest)

    # Create additional demo users
    demo_users = [
        ('sarah_m', 'sarah@email.com'),
        ('mike_t', 'mike@email.com'),
        ('jenny_l', 'jenny@email.com'),
        ('alex_k', 'alex@email.com'),
        ('chris_b', 'chris@email.com')
    ]

    for username, email in demo_users:
        user = User(username=username, email=email)
        user.set_password('demo123')
        db.session.add(user)

    db.session.commit()

    # Create sample reviews
    reviews_data = [
        (1, 2, 5, 'Amazing experience!', 'The food was incredible and the service was top-notch. Highly recommend the seasonal tasting menu.'),
        (1, 3, 4, 'Great atmosphere', 'Beautiful restaurant with delicious farm-fresh dishes. A bit pricey but worth it for special occasions.'),
        (2, 4, 5, 'Found unique gifts', 'So many wonderful handcrafted items! I found the perfect birthday present for my mom.'),
        (3, 5, 5, 'Best haircut ever', 'The stylists here really listen to what you want. Walked out feeling like a million bucks!'),
        (3, 6, 4, 'Relaxing spa day', 'Booked a full spa package and it was heavenly. Only minor issue was the wait time.'),
        (4, 2, 5, 'Nostalgia overload!', 'Love this place! They have all the classic arcade games from my childhood plus new VR stuff.'),
        (5, 3, 5, 'Life-changing yoga', 'The instructors are amazing. I have been coming for 6 months and my flexibility has improved so much.'),
        (6, 4, 4, 'Coffee perfection', 'Best espresso in town. The baristas really know their craft. Gets busy on weekends.'),
        (6, 5, 5, 'My daily stop', 'Cannot start my day without their cold brew. The pastries are freshly baked too!'),
        (7, 6, 4, 'Plant paradise', 'Huge selection of plants and the staff gave me great advice for my balcony garden.'),
        (8, 2, 5, 'Fixed my laptop fast', 'Brought in my laptop with a broken screen, had it back the next day. Great service!'),
        (9, 3, 4, 'Unique film selection', 'Love discovering indie films here. The craft beer selection is a nice bonus.'),
        (10, 4, 5, 'Best gym around', 'Clean facilities, modern equipment, and the trainers really push you to improve.'),
        (11, 5, 5, 'Authentic Italian', 'Feels like being in Italy! The homemade pasta is incredible.'),
        (12, 6, 5, 'Book lover heaven', 'Such a cozy shop with excellent recommendations. The author events are wonderful.')
    ]

    for business_id, user_id, rating, title, content in reviews_data:
        review = Review(
            business_id=business_id,
            user_id=user_id,
            rating=rating,
            title=title,
            content=content
        )
        db.session.add(review)

    db.session.commit()

    # Create sample deals
    deals_data = [
        (1, '20% Off Dinner', 'Get 20% off your entire dinner bill', 'percentage', 20, 'RUSTIC20', 30, 'Valid Sunday-Thursday. Cannot be combined with other offers.'),
        (3, 'Free Conditioning Treatment', 'Complimentary deep conditioning with any haircut', 'bogo', None, 'BLOOM2024', 45, 'First-time customers only.'),
        (4, '$5 Off Gaming Session', 'Save $5 on any 2-hour gaming session', 'fixed', 5, 'PIXEL5', 60, 'One per customer per day.'),
        (5, 'First Class Free', 'Try your first yoga class absolutely free', 'percentage', 100, 'ZENITHFREE', 90, 'New members only. Must register online.'),
        (6, 'Buy One Get One Coffee', 'Buy any drink, get a second of equal or lesser value free', 'bogo', None, 'GRIND2FOR1', 14, 'Valid before 10am only.'),
        (10, 'No Enrollment Fee', 'Join now with zero enrollment fee', 'fixed', 50, 'PEAKFIT', 30, 'Annual membership required.'),
        (11, 'Free Dessert', 'Complimentary tiramisu with any entree', 'bogo', None, 'DOLCE', 21, 'Dine-in only. One per table.'),
        (12, '15% Off Purchase', 'Save 15% on your total purchase', 'percentage', 15, 'READING15', 45, 'Excludes textbooks and special orders.')
    ]

    for business_id, title, desc, d_type, d_value, code, days, terms in deals_data:
        deal = Deal(
            business_id=business_id,
            title=title,
            description=desc,
            discount_type=d_type,
            discount_value=d_value,
            code=code,
            end_date=datetime.utcnow() + timedelta(days=days),
            terms=terms
        )
        db.session.add(deal)

    db.session.commit()
    print("Sample data initialized successfully!")


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()

        # Check if data exists, if not initialize
        if Business.query.count() == 0:
            init_sample_data()

    # Run the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
