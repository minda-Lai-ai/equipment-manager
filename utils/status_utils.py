from datetime import datetime

def status_light(status):
    return {
        "on": "🟢",
        "off": "🔴",
        "NA": "⚫"
    }.get(str(status).strip(), "⚫")

def maintenance_light(next_date_str):
    if next_date_str in ["", "NA"]:
        return "⚫"
    try:
        next_date = datetime.strptime(next_date_str, "%Y-%m-%d")
        today = datetime.today()
        delta = (next_date - today).days
        if delta < 0:
            return "��"
        elif delta <= 30:
            return "��"
        else:
            return "🟢"
    except:
        return "⚫"

