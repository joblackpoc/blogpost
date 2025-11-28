from django.contrib import admin
from .models import About, Service, Announcement, TeamMember, Location, ContactMessage, Position, Activity


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['title', 'phone', 'email', 'updated_at']
    search_fields = ['title', 'mission', 'vision']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'established_year')
        }),
        ('Mission & Vision', {
            'fields': ('mission', 'vision', 'history')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'working_hours')
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon', 'image')
        }),
        ('Details', {
            'fields': ('details', 'requirements', 'schedule')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'published_date', 'expiry_date', 'is_active', 'views']
    list_filter = ['priority', 'is_active', 'published_date']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'priority']
    date_hierarchy = 'published_date'
    readonly_fields = ['views', 'created_at', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'image')
        }),
        ('Settings', {
            'fields': ('priority', 'published_date', 'expiry_date', 'is_active')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name_th', 'name_en', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name_th', 'name_en']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Position Names', {
            'fields': ('name_th', 'name_en')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_display_position', 'email', 'phone', 'is_active', 'order']
    list_filter = ['position', 'is_active', 'joined_date']
    search_fields = ['name', 'bio', 'specialization']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'photo', 'bio')
        }),
        ('Position & Qualifications', {
            'fields': ('position', 'custom_position', 'specialization', 'qualifications', 'joined_date')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'is_main_office', 'is_active', 'order']
    list_filter = ['is_main_office', 'is_active']
    search_fields = ['name', 'address', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Contact Details', {
            'fields': ('address', 'phone', 'email', 'working_hours')
        }),
        ('Google Maps Integration', {
            'fields': ('latitude', 'longitude'),
            'description': '''<strong>Option 1 (Recommended):</strong> Paste the complete Google Maps embed URL from iframe src attribute.<br>
            Go to <a href="https://www.google.com/maps" target="_blank">Google Maps</a>, search for your location,
            click "Share" → "Embed a map" → Copy the URL from src="..." and paste below.<br><br>
            <strong>Option 2:</strong> Enter latitude and longitude coordinates (will auto-generate basic embed).'''
        }),
        ('Settings', {
            'fields': ('is_main_office', 'is_active', 'order')
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['subject', 'status', 'created_at']
    search_fields = ['name', 'email', 'message']
    list_editable = ['status']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'created_at')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Admin Actions', {
            'fields': ('status', 'admin_notes')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'activity_date', 'activity_time', 'get_location_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'activity_date', 'location', 'is_registration_required']
    search_fields = ['title', 'description', 'contact_person']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active']
    date_hierarchy = 'activity_date'
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'image')
        }),
        ('Date & Time', {
            'fields': ('activity_date', 'activity_time')
        }),
        ('Location', {
            'fields': ('location', 'custom_location')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_phone')
        }),
        ('Registration', {
            'fields': ('is_registration_required', 'max_participants')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )
