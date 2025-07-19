from django.core.exceptions import ValidationError
from django.conf import settings
from string import punctuation


class PasswordComplexityValidator:
    def __init__(self, complexity=settings.PASSWORD_COMPLEXITY):
        self.complexity = complexity

    def validate(self, password: str, user=None):
        if self.complexity is None:
            return

        current_complexity = {
            "UPPERCASE": 0,
            "LOWERCASE": 0,
            "DIGITS": 0,
            "SPECIALS": 0
        }

        for char in password:
            if char.isupper():
                current_complexity["UPPERCASE"] += 1
            elif char.islower():
                current_complexity["LOWERCASE"] += 1
            elif char.isdigit():
                current_complexity["DIGITS"] += 1
            elif char in punctuation:
                current_complexity["SPECIALS"] += 1
            else:
                raise ValidationError(
                    "出现非法字符，口令由大小写字母、数字及特殊符号构成",
                    code="password_invalid_character"
                )

        errors = []
        if current_complexity["UPPERCASE"] < self.complexity["UPPERCASE"]:
            errors.append(f"至少包含{self.complexity['UPPERCASE']}个大写字母")

        if current_complexity["LOWERCASE"] < self.complexity["LOWERCASE"]:
            errors.append(f"至少包含{self.complexity['LOWERCASE']}个小写字母")

        if current_complexity["DIGITS"] < self.complexity["DIGITS"]:
            errors.append(f"至少包含{self.complexity['DIGITS']}个数字")

        if current_complexity["SPECIALS"] < self.complexity["SPECIALS"]:
            errors.append(f"至少包含{self.complexity['SPECIALS']}个特殊字符")

        if errors:
            raise ValidationError(
                "\n".join(errors),
                code="password_complexity_not_enough"
            )

    def get_help_text(self):
        return "口令必须满足复杂度要求"
