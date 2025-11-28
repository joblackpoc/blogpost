from django.db import models
from django.utils.text import slugify
from security.validators import validate_no_sql_injection


class About(models.Model):
    """Information about the Public Health Center"""
    title = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    mission = models.TextField(help_text="Mission statement")
    vision = models.TextField(help_text="Vision statement")
    history = models.TextField(blank=True, help_text="Organization history")
    description = models.TextField(help_text="General description")
    established_year = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField()
    working_hours = models.TextField(help_text="e.g., Mon-Fri: 8:00 AM - 4:30 PM")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"

    def __str__(self):
        return self.title


class Service(models.Model):
    """Health services offered by the center"""
    name = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="fa-heartbeat",
                           help_text="FontAwesome icon class (e.g., fa-heartbeat, fa-syringe)")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    details = models.TextField(blank=True, help_text="Extended service details")
    requirements = models.TextField(blank=True, help_text="What patients need to bring")
    schedule = models.CharField(max_length=200, blank=True, help_text="Service availability schedule")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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
    content = models.TextField()
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
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def is_expired(self):
        """Check if announcement is expired"""
        if self.expiry_date:
            from django.utils import timezone
            return timezone.now().date() > self.expiry_date
        return False


class TeamMember(models.Model):
    """Staff and team members"""
    POSITION_CHOICES = [
        ('director', 'Director'),
        ('deputy_director', 'Deputy Director'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('pharmacist', 'Pharmacist'),
        ('dentist', 'Dentist'),
        ('admin', 'Administrative Staff'),
        ('technician', 'Medical Technician'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    custom_position = models.CharField(max_length=200, blank=True,
                                      help_text="Use this for positions not in the list")
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    bio = models.TextField(blank=True)
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
        """Return custom position if set, otherwise return position choice"""
        return self.custom_position if self.custom_position else self.get_position_display()


class Location(models.Model):
    """Physical locations and branches"""
    name = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True,
                                   help_text="Google Maps latitude coordinate (optional if using embed_map_url)")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True,
                                    help_text="Google Maps longitude coordinate (optional if using embed_map_url)")
    google_maps_embed = models.TextField(blank=True,
                                         help_text='Paste the complete Google Maps embed URL from iframe src (e.g., https://www.google.com/maps/embed?pb=...)')
    working_hours = models.TextField()
    is_main_office = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True, help_text="Additional location details")
    image = models.ImageField(upload_to='locations/', blank=True, null=True)

    class Meta:
        ordering = ['-is_main_office', 'order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {'(Main Office)' if self.is_main_office else ''}"

    def get_google_maps_url(self):
        """Generate Google Maps URL for this location"""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return "#"

    def get_google_maps_embed_url(self):
        """Get Google Maps embed URL from the stored field or generate from coordinates"""
        if self.google_maps_embed:
            return self.google_maps_embed
        elif self.latitude and self.longitude:
            return f"https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d1000!2d{self.longitude}!3d{self.latitude}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2s!4v1234567890"
        return None


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
