import os

ACCOUNT_IDS = {
    "BILLS": os.getenv("BILLS"),
    "GIFTS": os.getenv("GIFTS"),
    "KIDS": os.getenv("KIDS"),
    "EXTRAS": os.getenv("EXTRAS"),
    "HOLIDAYS": os.getenv("HOLIDAYS"),
    "SUPER": os.getenv("SUPER"),
    "INVESTMENTS": os.getenv("INVESTMENTS"),
    "RAINY_DAY": os.getenv("RAINY_DAY"),
    "EMERGENCY": os.getenv("EMERGENCY"),
    "HOME_DEPOSIT": os.getenv("HOME_DEPOSIT"),
    "TRANSPORT": os.getenv("TRANSPORT"),
    "HEALTH": os.getenv("HEALTH"),
    "GROCERIES": os.getenv("GROCERIES"),
    "PERSONAL_SAVER": os.getenv("PERSONAL_SAVER"),
    "RENT": os.getenv("RENT"),
    "2UP": os.getenv("2UP"),
    "IC_INDIVIDUAL": os.getenv("IC_INDIVIDUAL"),
}

CATEGORIES = ["personal", "good-life", "home", "transport"]

NOTION_API_KEY = os.getenv("NOTION_API_KEY")

DATABASE_ID = os.getenv("DATABASE_ID")
