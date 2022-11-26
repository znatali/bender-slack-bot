LEAVE_MODAL = [
    {
        "type": "section",
        "block_id": "input_mode",
        "text": {
            "type": "mrkdwn",
            "text": "*What you're leaving for?*"
        },
        "accessory": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select an item",
                "emoji": True
            },
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Sick 🤧",
                        "emoji": True
                    },
                    "value": "value-0"
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Day off 😎",
                        "emoji": True
                    },
                    "value": "value-1"
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Vacation 🤠",
                        "emoji": True
                    },
                    "value": "value-2"
                }
            ],
            "action_id": "reason_view_id"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "How long you're planing be off?"
        }
    },
    {
        "type": "actions",
        "block_id": "input_datas",
        "elements": [
            {
                "type": "datepicker",
                "initial_date": "1990-04-28",
                "placeholder": {
                    "type": "plain_text",
                    "text": "From",
                },
                "action_id": "actionId-0"
            },
            {
                "type": "datepicker",
                "initial_date": "1990-04-28",
                "placeholder": {
                    "type": "plain_text",
                    "text": "To",
                },
                "action_id": "actionId-1"
            }
        ]
    },
]