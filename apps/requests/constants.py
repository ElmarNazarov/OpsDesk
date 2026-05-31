DEFAULT_CATEGORIES = [
    {
        "name": "Vacation",
        "slug": "vacation",
        "description": "Time off and vacation requests",
        "requires_manager_approval": True,
        "requires_ops_approval": False,
        "requires_hr_approval": True,
    },
    {
        "name": "Equipment",
        "slug": "equipment",
        "description": "Hardware and equipment requests",
        "requires_manager_approval": True,
        "requires_ops_approval": True,
        "requires_hr_approval": False,
    },
    {
        "name": "Software Access",
        "slug": "software-access",
        "description": "Software licenses and access",
        "requires_manager_approval": True,
        "requires_ops_approval": True,
        "requires_hr_approval": False,
    },
    {
        "name": "Remote Work",
        "slug": "remote-work",
        "description": "Remote work arrangements",
        "requires_manager_approval": True,
        "requires_ops_approval": False,
        "requires_hr_approval": True,
    },
    {
        "name": "Reimbursement",
        "slug": "reimbursement",
        "description": "Expense reimbursements",
        "requires_manager_approval": True,
        "requires_ops_approval": False,
        "requires_hr_approval": False,
    },
    {
        "name": "General Support",
        "slug": "general-support",
        "description": "General support requests",
        "requires_manager_approval": False,
        "requires_ops_approval": False,
        "requires_hr_approval": False,
    },
]

FINAL_STATUSES = ["REJECTED", "FULFILLED", "CANCELLED"]
