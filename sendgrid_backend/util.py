import sendgrid

SENDGRID_VERSION = sendgrid.__version__

SENDGRID_5 = SENDGRID_VERSION < '6'
SENDGRID_6 = SENDGRID_VERSION >= '6'
