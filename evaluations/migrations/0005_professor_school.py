# Generated migration to add school field to professor

from django.db import migrations, models
import django.db.models.deletion


def copy_department_to_school(apps, schema_editor):
    """Copy each professor's department's school to their school field"""
    Professor = apps.get_model('evaluations', 'Professor')
    Department = apps.get_model('evaluations', 'Department')
    
    for professor in Professor.objects.all():
        if professor.department_id:
            try:
                department = Department.objects.get(id=professor.department_id)
                professor.school_id = department.school_id
                professor.save()
            except Department.DoesNotExist:
                pass


def reverse_copy(apps, schema_editor):
    """This is a one-way migration, no reverse possible without data loss"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0004_school_alter_department_options_and_more'),
    ]

    operations = [
        # Step 1: Add school field as nullable first
        migrations.AddField(
            model_name='professor',
            name='school',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='professors',
                to='evaluations.school',
                verbose_name='School'
            ),
        ),
        # Step 2: Copy data from department to school
        migrations.RunPython(copy_department_to_school, reverse_copy),
        # Step 3: Make school field non-nullable
        migrations.AlterField(
            model_name='professor',
            name='school',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='professors',
                to='evaluations.school',
                verbose_name='School'
            ),
        ),
        # Step 4: Remove department field
        migrations.RemoveField(
            model_name='professor',
            name='department',
        ),
    ]
