# ==========================================
# USER ERROR
# ==========================================


class UserError(Exception):
    """Raise when a user tries to register with a taken username or email."""

    pass


# ==========================================
# TRIP ERROR
# ==========================================


class TripError(Exception):
    pass


# ==========================================
# EXPENSE ERROR
# ==========================================


class ExpenseError(Exception):
    pass
