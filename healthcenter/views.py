from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import About, Service, Announcement, TeamMember, Location, Position, Activity
from .forms import ContactForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ServiceForm, AnnouncementForm, LocationForm, TeamMemberForm, PositionForm, ActivityForm
from django import template
from django.contrib.auth.decorators import login_required, user_passes_test

register = template.Library()

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

    # Get upcoming activities
    activities = Activity.objects.filter(
        is_active=True,
        activity_date__gte=today
    ).order_by('activity_date')[:4]

    context = {
        'about': about,
        'services': services,
        'announcements': announcements,
        'team_members': team_members,
        'locations': locations,
        'activities': activities,
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

# Utility for field access in template
@register.filter
def get_field(obj, field):
    return getattr(obj, field)

# Service CRUD with pagination, search, messages
class ServiceListView(ListView):
    model = Service
    template_name = 'healthcenter/crud/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Services'
        context['columns'] = ['Name', 'Description', 'Active', 'Order']
        context['fields'] = ['name', 'description', 'is_active', 'order']
        context['create_url'] = reverse_lazy('healthcenter:service_create')
        context['back_url'] = reverse_lazy('healthcenter:home')
        context['messages'] = messages.get_messages(self.request)
        context['perms'] = self.request.user.is_authenticated
        return context

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'healthcenter/service_detail.html'
    context_object_name = 'service'

class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:service_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Service'
        context['cancel_url'] = reverse_lazy('healthcenter:service_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Service created successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating service.')
        return super().form_invalid(form)

class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:service_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Service'
        context['cancel_url'] = reverse_lazy('healthcenter:service_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Service updated successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating service.')
        return super().form_invalid(form)

class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Service
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:service_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Service'
        context['cancel_url'] = reverse_lazy('healthcenter:service_list')
        return context
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Service deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Announcement CRUD
class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'healthcenter/crud/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Announcements'
        context['columns'] = ['Title', 'Priority', 'Published', 'Active']
        context['fields'] = ['title', 'priority', 'published_date', 'is_active']
        context['create_url'] = reverse_lazy('healthcenter:announcement_create')
        context['back_url'] = reverse_lazy('healthcenter:home')
        context['messages'] = messages.get_messages(self.request)
        context['perms'] = self.request.user.is_authenticated
        return context

class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'healthcenter/announcement_detail.html'
    context_object_name = 'announcement'

class AnnouncementCreateView(LoginRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:announcement_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Announcement'
        context['cancel_url'] = reverse_lazy('healthcenter:announcement_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Announcement created successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating announcement.')
        return super().form_invalid(form)

class AnnouncementUpdateView(LoginRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:announcement_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Announcement'
        context['cancel_url'] = reverse_lazy('healthcenter:announcement_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Announcement updated successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating announcement.')
        return super().form_invalid(form)

class AnnouncementDeleteView(LoginRequiredMixin, DeleteView):
    model = Announcement
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:announcement_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Announcement'
        context['cancel_url'] = reverse_lazy('healthcenter:announcement_list')
        return context
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Announcement deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Location CRUD
class LocationListView(ListView):
    model = Location
    template_name = 'healthcenter/crud/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Locations'
        context['columns'] = ['Name', 'Address', 'Phone', 'Active']
        context['fields'] = ['name', 'address', 'phone', 'is_active']
        context['create_url'] = reverse_lazy('healthcenter:location_create')
        context['back_url'] = reverse_lazy('healthcenter:home')
        context['messages'] = messages.get_messages(self.request)
        context['perms'] = self.request.user.is_authenticated
        return context

class LocationDetailView(DetailView):
    model = Location
    template_name = 'healthcenter/location_detail.html'
    context_object_name = 'location'

class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:location_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Location'
        context['cancel_url'] = reverse_lazy('healthcenter:location_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Location created successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating location.')
        return super().form_invalid(form)

class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:location_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Location'
        context['cancel_url'] = reverse_lazy('healthcenter:location_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Location updated successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating location.')
        return super().form_invalid(form)

class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:location_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Location'
        context['cancel_url'] = reverse_lazy('healthcenter:location_list')
        return context
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Location deleted successfully.')
        return super().delete(request, *args, **kwargs)

# TeamMember CRUD
class TeamMemberListView(ListView):
    model = TeamMember
    template_name = 'healthcenter/crud/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Team Members'
        context['columns'] = ['Name', 'Position', 'Email', 'Active']
        context['fields'] = ['name', 'position', 'email', 'is_active']
        context['create_url'] = reverse_lazy('healthcenter:teammember_create')
        context['back_url'] = reverse_lazy('healthcenter:home')
        context['messages'] = messages.get_messages(self.request)
        context['perms'] = self.request.user.is_authenticated
        return context

class TeamMemberDetailView(DetailView):
    model = TeamMember
    template_name = 'healthcenter/teammember_detail.html'
    context_object_name = 'teammember'

class TeamMemberCreateView(LoginRequiredMixin, CreateView):
    model = TeamMember
    form_class = TeamMemberForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:teammember_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Team Member'
        context['cancel_url'] = reverse_lazy('healthcenter:teammember_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Team member created successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating team member.')
        return super().form_invalid(form)

class TeamMemberUpdateView(LoginRequiredMixin, UpdateView):
    model = TeamMember
    form_class = TeamMemberForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:teammember_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Team Member'
        context['cancel_url'] = reverse_lazy('healthcenter:teammember_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Team member updated successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating team member.')
        return super().form_invalid(form)

class TeamMemberDeleteView(LoginRequiredMixin, DeleteView):
    model = TeamMember
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:teammember_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Team Member'
        context['cancel_url'] = reverse_lazy('healthcenter:teammember_list')
        return context
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Team member deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Position CRUD
class PositionListView(ListView):
    model = Position
    template_name = 'healthcenter/crud/list.html'
    context_object_name = 'object_list'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name_th__icontains=search) | qs.filter(name_en__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Positions'
        context['columns'] = ['Thai Name', 'English Name', 'Order', 'Active']
        context['fields'] = ['name_th', 'name_en', 'order', 'is_active']
        context['create_url'] = reverse_lazy('healthcenter:position_create')
        context['back_url'] = reverse_lazy('healthcenter:dashboard')
        context['messages'] = messages.get_messages(self.request)
        context['perms'] = self.request.user.is_authenticated
        return context

class PositionDetailView(DetailView):
    model = Position
    template_name = 'healthcenter/position_detail.html'
    context_object_name = 'position'

class PositionCreateView(LoginRequiredMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:position_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Position'
        context['cancel_url'] = reverse_lazy('healthcenter:position_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Position created successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating position.')
        return super().form_invalid(form)

class PositionUpdateView(LoginRequiredMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:position_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Position'
        context['cancel_url'] = reverse_lazy('healthcenter:position_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Position updated successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating position.')
        return super().form_invalid(form)

class PositionDeleteView(LoginRequiredMixin, DeleteView):
    model = Position
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:position_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Position'
        context['cancel_url'] = reverse_lazy('healthcenter:position_list')
        return context
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Position deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Activity CRUD
class ActivityListView(ListView):
    model = Activity
    template_name = 'healthcenter/crud/list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Activities'
        context['columns'] = ['Title', 'Date', 'Time', 'Location', 'Active']
        context['fields'] = ['title', 'activity_date', 'activity_time', 'get_location_display', 'is_active']
        context['create_url'] = reverse_lazy('healthcenter:activity_create')
        context['back_url'] = reverse_lazy('healthcenter:dashboard')
        context['messages'] = messages.get_messages(self.request)
        context['perms'] = self.request.user.is_authenticated
        return context

class ActivityDetailView(DetailView):
    model = Activity
    template_name = 'healthcenter/activity_detail.html'
    context_object_name = 'activity'

class ActivityCreateView(LoginRequiredMixin, CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:activity_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Activity'
        context['cancel_url'] = reverse_lazy('healthcenter:activity_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Activity created successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating activity.')
        return super().form_invalid(form)

class ActivityUpdateView(LoginRequiredMixin, UpdateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:activity_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Activity'
        context['cancel_url'] = reverse_lazy('healthcenter:activity_list')
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Activity updated successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating activity.')
        return super().form_invalid(form)

class ActivityDeleteView(LoginRequiredMixin, DeleteView):
    model = Activity
    template_name = 'healthcenter/crud/form.html'
    success_url = reverse_lazy('healthcenter:activity_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Activity'
        context['cancel_url'] = reverse_lazy('healthcenter:activity_list')
        return context
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Activity deleted successfully.')
        return super().delete(request, *args, **kwargs)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def dashboard(request):
    return render(request, 'healthcenter/dashboard.html')
