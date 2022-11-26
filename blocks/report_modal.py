REPORT_MODAL = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Bender Report\n\n"
                    }
                },
                {
                    "type": "section",
                    "block_id": "input_mode",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*How are you today?*"
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
                                    "text": "🙂",
                                    "emoji": True
                                },
                                "value": "value-0"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "🙃",
                                    "emoji": True
                                },
                                "value": "value-1"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "🫠",
                                    "emoji": True
                                },
                                "value": "value-2"
                            }
                        ],
                        "action_id": "mood_view_id"
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_ytd",
                    "label": {
                        "type": "plain_text",
                        "text": "What you done yesterday?"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "yesterday_view_id",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter text"
                        }
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_td",
                    "label": {
                        "type": "plain_text",
                        "text": "What you're going do today?"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "today_view_id",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter text"
                        }
                    }
                }
            ]