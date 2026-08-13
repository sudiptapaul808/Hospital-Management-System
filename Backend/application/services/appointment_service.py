from datetime import datetime, timedelta

def validate_booking_slot(availability, start_datetime, end_datetime):
    start_window = datetime.combine(availability.date, availability.start_time)
    end_window = datetime.combine(availability.date, availability.end_time)

    selected_slot = (start_datetime, end_datetime)

    start = start_window
    while start < end_window:
        end = start + timedelta(minutes=30)
        slot = (start, end)
        if slot == selected_slot:
            return True
        start = end
    return False