from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Event, Booking, Comment, User
from .forms import CreateEventForm
from datetime import datetime
import uuid

views = Blueprint('views', __name__)


@views.route('/')
def index():
    # Redirect unauthenticated users to login
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return browse_events()

@views.route('/index')
@login_required
def browse_events():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').strip()
    
    query = Event.query
    
    if category != 'all' and category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            (Event.title.ilike(f'%{search}%')) |
            (Event.description.ilike(f'%{search}%')) |
            (Event.location.ilike(f'%{search}%'))
        )
    
    query = query.filter(Event.status.in_(['Open', 'Cancelled']))
    
    events = query.all()
    
    categories = db.session.query(Event.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('index.html', 
                         events=events, 
                         categories=categories,
                         current_category=category,
                         search_query=search)


@views.route('/event/new', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create new event"""
    form = CreateEventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            location=form.location.data,
            date=form.date.data,
            price=form.price.data,
            tickets_available=form.tickets_available.data,
            image=form.image.data or None,
            status='Open',
            user_id=current_user.id,
            acknowledgement_type=form.acknowledgement_type.data,
            acknowledgement_location=form.acknowledgement_location.data,
            acknowledgement_text=form.acknowledgement_text.data if form.acknowledgement_type.data != 'None' else None
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('views.event_details', event_id=event.id))
    
    return render_template('create_event.html', form=form)


@views.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Edit event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is event owner
    if event.user_id != current_user.id:
        flash('You can only edit your own events', 'danger')
        return redirect(url_for('views.event_details', event_id=event_id))
    
    form = CreateEventForm()
    
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.category = form.category.data
        event.location = form.location.data
        event.date = form.date.data
        event.price = form.price.data
        event.tickets_available = form.tickets_available.data
        event.image = form.image.data or None
        event.acknowledgement_type = form.acknowledgement_type.data
        event.acknowledgement_location = form.acknowledgement_location.data
        event.acknowledgement_text = form.acknowledgement_text.data if form.acknowledgement_type.data != 'None' else None
        
        db.session.commit()
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('views.event_details', event_id=event.id))
    
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.category.data = event.category
        form.location.data = event.location
        form.date.data = event.date
        form.price.data = event.price
        form.tickets_available.data = event.tickets_available
        form.image.data = event.image
        form.acknowledgement_type.data = event.acknowledgement_type
        form.acknowledgement_location.data = event.acknowledgement_location
        form.acknowledgement_text.data = event.acknowledgement_text
    
    return render_template('edit_event.html', form=form, event=event)


@views.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    """Cancel event"""
    event = Event.query.get_or_404(event_id)
    
    if event.user_id != current_user.id:
        flash('You can only cancel your own events', 'danger')
        return redirect(url_for('views.event_details', event_id=event_id))
    
    event.status = 'Cancelled'
    db.session.commit()
    
    flash('Event cancelled', 'info')
    return redirect(url_for('views.browse_events'))


@views.route('/event/<int:event_id>')
def event_details(event_id):
    """Display event details and comments"""
    event = Event.query.get_or_404(event_id)
    comments = Comment.query.filter_by(event_id=event_id).all()
    
    if current_user.is_authenticated:
        booking = Booking.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    return render_template('event_details.html', event=event, comments=comments, booking=booking)


@views.route('/event/<int:event_id>/book', methods=['POST'])
@login_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity <= 0 or quantity > event.tickets_available:
        flash('Invalid quantity', 'danger')
        return redirect(url_for('views.event_details', event_id=event_id))
    
    total_price = quantity * event.price
    
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    booking = Booking(
        order_id=order_id,
        quantity=quantity,
        total_price=total_price,
        booking_date=datetime.utcnow(),
        user_id=current_user.id,
        event_id=event_id
    )
    
    event.tickets_available -= quantity
    
    db.session.add(booking)
    db.session.commit()
    
    flash(f'Booking successful! Your Order ID: {order_id}', 'success')
    return redirect(url_for('views.booking_history'))


@views.route('/bookings')
@login_required
def booking_history():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('booking_history.html', bookings=bookings)


@views.route('/event/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    event = Event.query.get_or_404(event_id)
    text = request.form.get('text', '').strip()
    
    if not text:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('views.event_details', event_id=event_id))
    
    comment = Comment(
        text=text,
        comment_date=datetime.utcnow(),
        user_id=current_user.id,
        event_id=event_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added!', 'success')
    return redirect(url_for('views.event_details', event_id=event_id))


@views.route('/my-events')
@login_required
def my_events():
    """Display user's created events"""
    events = Event.query.filter_by(user_id=current_user.id).all()
    return render_template('my_events.html', events=events)


@views.route('/about-acknowledgement')
def about_acknowledgement():
    """Information page about Acknowledgement of Country"""
    custodians_info = {
        'Sydney': 'Eora Nation',
        'Melbourne': 'Kulin Nation',
        'Brisbane': 'Yuggera people',
        'Perth': 'Noongar people',
        'Adelaide': 'Kaurna people',
        'Canberra': 'Ngunnawal people',
        'Hobart': 'Palawa people',
        'Darwin': 'Larrakia people'
    }
    return render_template('about_acknowledgement.html', custodians=custodians_info)
