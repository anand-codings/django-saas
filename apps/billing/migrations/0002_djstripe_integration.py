# Generated migration for dj-stripe integration
# Restructures BillingCustomer as a linking table, removes Subscription/Invoice/PaymentMethod

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
        ("djstripe", "__latest__"),
        ("organizations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: Add new fields to BillingCustomer
        migrations.AddField(
            model_name="billingcustomer",
            name="djstripe_customer",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="billing_customer",
                to="djstripe.customer",
            ),
        ),
        # Change organization_id from UUID to proper FK
        migrations.RemoveField(
            model_name="billingcustomer",
            name="organization_id",
        ),
        migrations.AddField(
            model_name="billingcustomer",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="billing_customer",
                to="organizations.organization",
            ),
        ),
        # Step 2: Remove redundant fields from BillingCustomer
        migrations.RemoveField(
            model_name="billingcustomer",
            name="stripe_customer_id",
        ),
        migrations.RemoveField(
            model_name="billingcustomer",
            name="provider",
        ),
        migrations.RemoveField(
            model_name="billingcustomer",
            name="email",
        ),
        migrations.RemoveField(
            model_name="billingcustomer",
            name="name",
        ),
        migrations.RemoveField(
            model_name="billingcustomer",
            name="currency",
        ),
        migrations.RemoveField(
            model_name="billingcustomer",
            name="tax_id",
        ),
        # Step 3: Add check constraint
        migrations.AddConstraint(
            model_name="billingcustomer",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, organization__isnull=True)
                    | models.Q(user__isnull=True, organization__isnull=False)
                ),
                name="billing_customer_user_xor_org",
            ),
        ),
        # Step 4: Remove old models (Invoice depends on Subscription, so remove Invoice first)
        migrations.DeleteModel(
            name="Invoice",
        ),
        migrations.DeleteModel(
            name="PaymentMethod",
        ),
        # Step 5: Update UsageRecord FK from custom Subscription to djstripe.Subscription
        # First remove the old FK, then add the new one
        migrations.AlterField(
            model_name="usagerecord",
            name="subscription",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="usage_records",
                to="djstripe.subscription",
            ),
        ),
        # Step 6: Now we can safely remove old Subscription model
        migrations.DeleteModel(
            name="Subscription",
        ),
    ]
