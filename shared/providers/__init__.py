"""Abstract provider interfaces for cloud-agnostic service abstraction.

Each provider module defines an abstract base class. Concrete implementations
live in the respective app (e.g., apps.mailer has SESProvider, SendGridProvider).
"""
