from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import About, Service, Announcement, TeamMember, Location
from .forms import ContactForm


def home(request):
    """Landing page for Public Health Center"""
    try:
        about = About.objects.first()
    except About.DoesNotExist:
        about = None

    # Get active services
    services = Service.objects.filter(is_active=True)[:6]

    # Get active and non-expired announcements
    today = timezone.now().date()
    announcements = Announcement.objects.filter(
        is_active=True,
        published_date__lte=today
    ).exclude(
        expiry_date__lt=today
    )[:3]

    # Get active team members
    team_members = TeamMember.objects.filter(is_active=True)[:8]

    # Get locations
    locations = Location.objects.filter(is_active=True)

    context = {
        'about': about,
        'services': services,
        'announcements': announcements,
        'team_members': team_members,
        'locations': locations,
    }
    return render(request, 'healthcenter/home.html', context)


def about_us(request):
    """About Us page"""
    try:
        about = About.objects.first()
    except About.DoesNotExist:
        about = None

    team_members = TeamMember.objects.filter(is_active=True)

    context = {
        'about': about,
        'team_members': team_members,
    }
    return render(request, 'healthcenter/about.html', context)


def services(request):
    """Services listing page"""
    services_list = Service.objects.filter(is_active=True)

    context = {
        'services': services_list,
    }
    return render(request, 'healthcenter/services.html', context)


def service_detail(request, slug):
    """Individual service detail page"""
    service = get_object_or_404(Service, slug=slug, is_active=True)

    # Get related services
    related_services = Service.objects.filter(is_active=True).exclude(slug=slug)[:3]

    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'healthcenter/service_detail.html', context)


def announcements(request):
    """Announcements listing page"""
    today = timezone.now().date()
    announcements_list = Announcement.objects.filter(
        is_active=True,
        published_date__lte=today
    ).exclude(
        expiry_date__lt=today
    )

    context = {
        'announcements': announcements_list,
    }
    return render(request, 'healthcenter/announcements.html', context)


def announcement_detail(request, slug):
    """Individual announcement detail page"""
    announcement = get_object_or_404(Announcement, slug=slug, is_active=True)

    # Increment views
    announcement.views += 1
    announcement.save(update_fields=['views'])

    context = {
        'announcement': announcement,
    }
    return render(request, 'healthcenter/announcement_detail.html', context)


def team(request):
    """Team members listing page"""
    team_members = TeamMember.objects.filter(is_active=True)

    context = {
        'team_members': team_members,
    }
    return render(request, 'healthcenter/team.html', context)


def locations_view(request):
    """Locations listing page with Google Maps"""
    locations_list = Location.objects.filter(is_active=True)

    context = {
        'locations': locations_list,
    }
    return render(request, 'healthcenter/locations.html', context)


def contact(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for contacting us! We will respond to your message soon.')
            return redirect('healthcenter:contact')
    else:
        form = ContactForm()

    # Get main location for contact info
    try:
        main_location = Location.objects.filter(is_main_office=True, is_active=True).first()
    except Location.DoesNotExist:
        main_location = Location.objects.filter(is_active=True).first()

    try:
        about = About.objects.first()
    except About.DoesNotExist:
        about = None

    context = {
        'form': form,
        'main_location': main_location,
        'about': about,
    }
    return render(request, 'healthcenter/contact.html', context)
