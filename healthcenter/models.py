from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from security.validators import validate_no_sql_injection
from django_ckeditor_5.fields import CKEditor5Field

class About(models.Model):
    """Information about the Public Health Center"""
    title = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    mission = CKEditor5Field('Mission', config_name='extends', help_text="Mission statement")
    vision = CKEditor5Field('Vision', config_name='extends', help_text="Vision statement")
    history = CKEditor5Field('History', config_name='extends', blank=True, help_text="Organization history")
    description = CKEditor5Field('Description', config_name='extends', help_text="General description")
    established_year = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = CKEditor5Field('Address', config_name='extends')
    working_hours = CKEditor5Field('Working Hours', config_name='extends', help_text="e.g., Mon-Fri: 8:00 AM - 4:30 PM")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"

    def __str__(self):
        return self.title


class Service(models.Model):
    """Health services offered by the center"""
    name = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    from django.core.validators import RegexValidator
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Enter a valid "slug" consisting of letters, numbers, underscores or hyphens.'
            )
        ]
    )
    description = CKEditor5Field('Description', config_name='default')
    icon = models.CharField(max_length=50, default="fa-heartbeat",
                           help_text="FontAwesome icon class (e.g., fa-heartbeat, fa-syringe)")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    details = CKEditor5Field('Details', config_name='extends', blank=True, help_text="Extended service details")
    requirements = CKEditor5Field('Requirements', config_name='extends', blank=True, help_text="What patients need to bring")
    schedule = models.CharField(max_length=200, blank=True, help_text="Service availability schedule")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = f"service-{self.pk}" if self.pk else "service"
            self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('healthcenter:service_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('healthcenter:service_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('healthcenter:service_delete', kwargs={'pk': self.pk})


class Announcement(models.Model):
    """Public health announcements and news"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=300, validators=[validate_no_sql_injection])
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    content = CKEditor5Field('Content', config_name='default')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    published_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True, help_text="Announcement expires after this date")
    is_active = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date', '-priority']

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = f"announcement-{self.pk}" if self.pk else "announcement"
            self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def is_expired(self):
        """Check if announcement is expired"""
        if self.expiry_date:
            from django.utils import timezone
            return timezone.now().date() > self.expiry_date
        return False

    def get_absolute_url(self):
        return reverse('healthcenter:announcement_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('healthcenter:announcement_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('healthcenter:announcement_delete', kwargs={'pk': self.pk})


class Position(models.Model):
    """Staff positions/roles"""
    name_th = models.CharField(max_length=200, validators=[validate_no_sql_injection],
                               help_text="Position name in Thai", verbose_name="ชื่อตำแหน่ง (ไทย)")
    name_en = models.CharField(max_length=200, validators=[validate_no_sql_injection],
                               help_text="Position name in English", verbose_name="ชื่อตำแหน่ง (English)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name_th']
        verbose_name = "Position"
        verbose_name_plural = "Positions"

    def __str__(self):
        return f"{self.name_th} ({self.name_en})"

    def get_absolute_url(self):
        return reverse('healthcenter:position_detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('healthcenter:position_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('healthcenter:position_delete', kwargs={'pk': self.pk})


class TeamMember(models.Model):
    """Staff and team members"""
    name = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='team_members', verbose_name="ตำแหน่ง")
    custom_position = models.CharField(max_length=200, blank=True,
                                      help_text="Use this for positions not in the Position list",
                                      verbose_name="ตำแหน่งอื่นๆ (ถ้าไม่มีในรายการ)")
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    bio = CKEditor5Field('Bio', config_name='default')
    specialization = models.CharField(max_length=200, blank=True)
    qualifications = models.TextField(blank=True, help_text="Education and certifications")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.get_display_position()}"

    def get_display_position(self):
        """Return custom position if set, otherwise return position"""
        if self.custom_position:
            return self.custom_position
        elif self.position:
            return str(self.position)
        return "No Position"

    def get_absolute_url(self):
        return reverse('healthcenter:teammember_detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('healthcenter:teammember_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('healthcenter:teammember_delete', kwargs={'pk': self.pk})


class Location(models.Model):
    """Physical locations and branches"""
    name = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   help_text="Google Maps latitude coordinate", default=0.0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    help_text="Google Maps longitude coordinate", default=0.0)
    working_hours = models.TextField()
    is_main_office = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True, help_text="Additional location details")
    image = models.ImageField(upload_to='locations/', blank=True, null=True)

    class Meta:
        ordering = ['-is_main_office', 'order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = f"location-{self.pk}" if self.pk else "location"
            self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {'(Main Office)' if self.is_main_office else ''}"

    def get_google_maps_url(self):
        """Generate Google Maps URL for this location"""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"

    def get_google_maps_embed_url(self):
        """Generate Google Maps embed URL for iframe"""
        from django.conf import settings
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        if api_key:
            return f"https://www.google.com/maps/embed/v1/place?key={api_key}&q={self.latitude},{self.longitude}&zoom=15"
        return None  # Return None if no API key is configured

    def get_openstreetmap_embed_url(self):
        """Generate OpenStreetMap embed URL for iframe (no API key required)"""
        # OpenStreetMap embed using Leaflet.js
        return f"https://www.openstreetmap.org/export/embed.html?bbox={float(self.longitude)-0.01},{float(self.latitude)-0.01},{float(self.longitude)+0.01},{float(self.latitude)+0.01}&layer=mapnik&marker={self.latitude},{self.longitude}"

    def get_absolute_url(self):
        return reverse('healthcenter:location_detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('healthcenter:location_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('healthcenter:location_delete', kwargs={'pk': self.pk})


class ContactMessage(models.Model):
    """Contact form submissions"""
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('appointment', 'Appointment Request'),
        ('service', 'Service Information'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('resolved', 'Resolved'),
    ]

    name = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    message = models.TextField(validators=[validate_no_sql_injection])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, help_text="Internal notes (not visible to user)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"


class Activity(models.Model):
    """Health center activities and programs"""
    title = models.CharField(max_length=300, validators=[validate_no_sql_injection])
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    description = CKEditor5Field('Description', config_name='default', help_text="Brief description of the activity")
    image = models.ImageField(upload_to='activities/', blank=True, null=True)
    activity_date = models.DateField(help_text="Date of the activity")
    activity_time = models.CharField(max_length=100, blank=True, help_text="e.g., 9:00 AM - 3:00 PM")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='activities', help_text="Activity location")
    custom_location = models.CharField(max_length=200, blank=True,
                                      help_text="Custom location if not in Location list")
    contact_person = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    max_participants = models.IntegerField(null=True, blank=True,
                                          help_text="Maximum number of participants (leave empty for unlimited)")
    is_registration_required = models.BooleanField(default=False,
                                                   help_text="Whether registration is required")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-activity_date', 'title']
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = f"activity-{self.pk}" if self.pk else "activity"
            self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.activity_date})"

    def get_location_display(self):
        """Return custom location if set, otherwise return location"""
        if self.custom_location:
            return self.custom_location
        elif self.location:
            return str(self.location.name)
        return "Location TBA"

    def is_upcoming(self):
        """Check if activity is in the future"""
        from django.utils import timezone
        return self.activity_date >= timezone.now().date()

    def get_absolute_url(self):
        return reverse('healthcenter:activity_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('healthcenter:activity_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('healthcenter:activity_delete', kwargs={'pk': self.pk})
