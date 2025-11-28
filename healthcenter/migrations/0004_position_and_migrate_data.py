# Generated migration with custom data migration

from django.db import migrations, models
import django.db.models.deletion
from security.validators import validate_no_sql_injection


def migrate_positions_forward(apps, schema_editor):
    """Migrate old position choices to new Position model"""
    Position = apps.get_model('healthcenter', 'Position')
    TeamMember = apps.get_model('healthcenter', 'TeamMember')

    # Create default positions from old choices
    positions_map = {
        'ผู้อำนวยการ': 'Director',
        'รองผู้อำนวยการ': 'Deputy Director',
        'แพทย์': 'Doctor',
        'พยาบาล': 'Nurse',
        'เภสัชกร': 'Pharmacist',
        'ทันตแพทย์': 'Dentist',
        'เจ้าหน้าที่บริหาร': 'Administrative Staff',
        'เจ้าหน้าที่เทคนิค': 'Medical Technician',
        'อื่นๆ': 'Other',
    }

    # Create Position objects
    created_positions = {}
    for idx, (th_name, en_name) in enumerate(positions_map.items(), start=1):
        pos = Position.objects.create(
            name_th=th_name,
            name_en=en_name,
            order=idx,
            is_active=True
        )
        created_positions[th_name] = pos

    # Migrate existing TeamMember data
    for member in TeamMember.objects.all():
        old_position = getattr(member, 'position_old', None)
        if old_position and old_position in created_positions:
            # Found matching position, use it
            member.custom_position = ''  # Clear custom since we have a real position
        elif old_position:
            # Position not in our list, move to custom_position
            member.custom_position = old_position
        member.save()


def migrate_positions_backward(apps, schema_editor):
    """Reverse migration - move Position back to choices"""
    TeamMember = apps.get_model('healthcenter', 'TeamMember')

    for member in TeamMember.objects.all():
        if member.position:
            member.custom_position = str(member.position)
            member.save()


class Migration(migrations.Migration):

    dependencies = [
        ('healthcenter', '0003_remove_location_google_maps_embed_and_more'),
    ]

    operations = [
        # Step 1: Create Position model
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_th', models.CharField(help_text='Position name in Thai', max_length=200, validators=[validate_no_sql_injection], verbose_name='ชื่อตำแหน่ง (ไทย)')),
                ('name_en', models.CharField(help_text='Position name in English', max_length=200, validators=[validate_no_sql_injection], verbose_name='ชื่อตำแหน่ง (English)')),
                ('order', models.IntegerField(default=0, help_text='Display order (lower numbers first)')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Position',
                'verbose_name_plural': 'Positions',
                'ordering': ['order', 'name_th'],
            },
        ),

        # Step 2: Rename old position field to position_old temporarily
        migrations.RenameField(
            model_name='teammember',
            old_name='position',
            new_name='position_old',
        ),

        # Step 3: Add new position ForeignKey field
        migrations.AddField(
            model_name='teammember',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_members', to='healthcenter.position', verbose_name='ตำแหน่ง'),
        ),

        # Step 4: Update custom_position field
        migrations.AlterField(
            model_name='teammember',
            name='custom_position',
            field=models.CharField(blank=True, help_text='Use this for positions not in the Position list', max_length=200, verbose_name='ตำแหน่งอื่นๆ (ถ้าไม่มีในรายการ)'),
        ),

        # Step 5: Migrate data
        migrations.RunPython(migrate_positions_forward, migrate_positions_backward),

        # Step 6: Remove the old position_old field
        migrations.RemoveField(
            model_name='teammember',
            name='position_old',
        ),
    ]
