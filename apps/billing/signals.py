"""Internal Django signals for billing events.

Other apps can connect to these signals without importing billing internals.
Webhook handlers in webhooks.py fire these after processing Stripe events.
"""

import django.dispatch

# Fired when a subscription becomes active (new or reactivated)
subscription_activated = django.dispatch.Signal()

# Fired when a subscription is canceled or expires
subscription_canceled = django.dispatch.Signal()

# Fired when a payment fails
payment_failed = django.dispatch.Signal()

# Fired when a trial is about to end (~3 days before)
trial_ending = django.dispatch.Signal()
