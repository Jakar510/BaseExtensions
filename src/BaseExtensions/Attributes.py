import re




__all__ = [
        'IsAttributePrivate',
        ]

private_or_special_function_searcher = re.compile(r"(^__\w+$)|(^_\w+$)|(^__\w+__$)")

def IsAttributePrivate(attr_name: str) -> bool: return private_or_special_function_searcher.search(attr_name) is not None
