from typing import Dict, Any

def get_user_mention(user_data: Dict[str, Any]) -> str:
    """
    Generates a user mention link from user data dictionary.
    """
    user_id = user_data.get("id")
    username = user_data.get("username")
    first_name = user_data.get("first_name")

    if username:
        return f"@{username}"
    
    # Fallback to first_name link if no username
    name = first_name if first_name else f"User {user_id}"
    return f'<a href="tg://user?id={user_id}">{name}</a>' 