def obfuscate_phone_number(phone: str) -> str:
    """
    Obfuscates a phone number by replacing middle digits with asterisks.
    Standard BD phone is 11 digits (e.g., 01712345678 -> 017*****678).
    """
    if not phone:
        return ""
    # BD phone is 11 digits, but some might be stored with +880
    min_phone_len = 10
    if len(phone) >= min_phone_len:
        return f"{phone[:3]}*****{phone[-3:]}"
    return phone


def obfuscate_name(name: str) -> str:
    """
    Obfuscates a name by returning only initials for first/middle names
    and the full last name. If no name is provided, returns 'Donor'.
    """
    if not name:
        return "Donor"
    parts = name.strip().split()
    if len(parts) > 1:
        initials = " ".join([f"{p[0]}." for p in parts[:-1]])
        return f"{initials} {parts[-1]}"
    return name
