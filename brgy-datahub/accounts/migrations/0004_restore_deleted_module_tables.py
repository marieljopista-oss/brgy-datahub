from django.db import migrations


def restore_deleted_module_tables(apps, schema_editor):
    existing_tables = set(schema_editor.connection.introspection.table_names())
    model_names = [
        'LandBody',
        'WaterBody',
        'Utility',
        'Building',
        'Facility',
        'RoadNetwork',
        'Institution',
        'MedicalStaff',
        'Professional',
    ]

    for model_name in model_names:
        model = apps.get_model('accounts', model_name)
        if model._meta.db_table not in existing_tables:
            schema_editor.create_model(model)
            existing_tables.add(model._meta.db_table)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_household_head_alter_household_household_id_and_more'),
    ]

    operations = [
        migrations.RunPython(restore_deleted_module_tables, migrations.RunPython.noop),
    ]
