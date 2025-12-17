class ValidationException(Exception):
    def __init__(self, field_name, message):
        super().__init__(f"{field_name}: {message}")
        self.field_name = field_name
        self.message = message

class ValidateIntException(ValidationException):
    def __init__(self, field_name):
        super().__init__(field_name, "")

    def check(self, value, min_val=None, max_val=None):
        if not value or not value.strip():
            raise ValidationException(self.field_name, "cannot be empty")

        stripped_value = value.strip()
        if stripped_value.startswith('-'):
            raise ValidationException(self.field_name, "cannot be negative")
        
        if not stripped_value.isdigit():
            raise ValidationException(self.field_name, "must be numeric")

        num = int(stripped_value)

        if min_val is not None and num < min_val:
            raise ValidationException(self.field_name, f"must be >= {min_val}")

        if max_val is not None and num > max_val:
            raise ValidationException(self.field_name, f"must be <= {max_val}")

        return num

class ValidateRangeException(ValidationException):
    def check(self, number, min_val, max_val):
        if number < min_val or number > max_val:
            raise ValidationException(self.field_name,
                                      f"must be between {min_val} and {max_val}")
        return number


class ValidateTextException(ValidationException):
    def __init__(self, field_name):
        super().__init__(field_name, "")

    def check(self, value, min_len=1, max_len=100, existing_names=None):
        if not value or not value.strip():
            raise ValidationException(self.field_name, "cannot be empty")

        value = value.strip()

        if len(value) < min_len:
            raise ValidationException(self.field_name,
                                     f"must be at least {min_len} characters")

        if len(value) > max_len:
            raise ValidationException(self.field_name,
                                     f"must be <= {max_len} characters")
        
        for char in value:
            if not (char.isalnum() or char.isspace()):
                raise ValidationException(self.field_name,
                                         f"contains invalid character: '{char}' (only letters, numbers and spaces allowed)")

        if value.replace(' ', '').isdigit():
            raise ValidationException(self.field_name, "cannot consist only of numbers")

        has_letter = False
        for char in value:
            if char.isalpha():
                has_letter = True
                break
        
        if not has_letter:
            raise ValidationException(self.field_name, "must contain at least one letter")
        
        if existing_names is not None:
            value_lower = value.lower()
            for existing in existing_names:
                if existing.lower() == value_lower:
                    raise ValidationException(self.field_name,
                                             f"'{value}' already exists")
                
        return value
    
class ValidateUniqueNumberException(ValidationException):
    def __init__(self, field_name):
        super().__init__(field_name, "")
    
    def check(self, value, existing_numbers, check_global=False, all_numbers=None):
        value = str(value).strip()
        if not value.isdigit():
            raise ValidationException(self.field_name, "must be a number")
        
        num = int(value)
        if num < 1:
            raise ValidationException(self.field_name, "must be >= 1")
        
        if num in existing_numbers:
            raise ValidationException(self.field_name, f"{num} already exists in this collection")
        
        if check_global:
            if all_numbers is None:
                raise ValidationException(self.field_name, "global numbers list required for global check")
            
            if num in all_numbers:
                raise ValidationException(self.field_name, f"{num} already exists in another collection")
        
        return num
    
class ValidatePageNumberException(ValidationException):
    def __init__(self, field_name):
        super().__init__(field_name, "")
    
    def check(self, value, existing_numbers, check_order=False, allow_global_duplicate=False):
        value = str(value).strip()
        
        if not value.isdigit():
            raise ValidationException(self.field_name, "must be a number")
        
        num = int(value)

        if num < 1:
            raise ValidationException(self.field_name, "must be >= 1")
        
        if num in existing_numbers:
            raise ValidationException(self.field_name, f"{num} already exists in this collection")

        if check_order and existing_numbers:
            max_existing = max(existing_numbers)
            if num != max_existing + 1:
                raise ValidationException(self.field_name, 
                                         f"must be {max_existing + 1} (next after page {max_existing})")
        
        return num