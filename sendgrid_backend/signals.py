import django.dispatch

sendgrid_email_sent = django.dispatch.Signal(providing_args=["message", "fail_flag"])
