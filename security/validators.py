from django.core.exceptions import ValidationError
import logging
import re

logger = logging.getLogger('security')

def validate_no_sql_injection(value):
    patterns = [r"(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)", r"(--|#)", r"(OR.*=.*)", r"(AND.*=.*)"]
    for pattern in patterns:
        if re.search(pattern, str(value), re.IGNORECASE):
            logger.warning(f'SQL injection attempt: {value}')
            raise ValidationError('Invalid input')

def validate_no_command_injection(value):
    dangerous = ['|', '&', ';', '$', '`', '\n', '(', ')', '<', '>']
    for char in dangerous:
        if char in str(value):
            logger.warning(f'Command injection attempt: {value}')
            raise ValidationError('Invalid characters')

def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1].lower()
    allowed = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']
    if ext not in allowed:
        raise ValidationError(f'Extension {ext} not allowed')

def validate_file_content(value):
    return True  # Simplified - would use python-magic in production
