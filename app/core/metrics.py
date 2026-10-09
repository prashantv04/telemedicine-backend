from prometheus_client import Counter

# Booking metrics
booking_created_total = Counter(
    "booking_created_total",
    "Total number of bookings created"
)

# # Payment metrics
# payment_succeeded_total = Counter(
#     "payment_succeeded_total",
#     "Total number of successful payments"
# )
#
# # Consultation metrics
# consultation_completed_total = Counter(
#     "consultation_completed_total",
#     "Total number of completed consultations"
# )