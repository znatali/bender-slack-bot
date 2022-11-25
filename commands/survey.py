

def regular_report(views_values,name):
    mood = views_values['input_mode']['mood_view_id']['selected_option']['text']['text']
    yesterday_dids = views_values['input_ytd']['yesterday_view_id']['value']
    today_dids = views_values['input_td']['today_view_id']['value']

    # Do whatever you want with the input data - here we're saving it to a DB
    # then sending the user a verification of their submission

    # Message to send user
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Bender {name} reports:",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Done:*",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{yesterday_dids}",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*In a mood  {mood}  to do:*",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{today_dids}",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Motivational picture*",
            }
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "I Need a Marg",
            },
            "image_url": "https://assets3.thrillist.com/v1/image/1682388/size/tl-horizontal_main.jpg",
            "alt_text": "marg"
        }
    ]



def leave_report(views_values, name):
    reason = views_values['input_mode']['reason_view_id']['selected_option']['text']['text']
    from_leave = views_values['input_datas']['actionId-0']['selected_date']
    to_leave = views_values['input_datas']['actionId-1']['selected_date']

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Bender {name} leave reports:",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Leaving for *{reason}* from {from_leave} to {to_leave}",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Motivational picture*",
            }
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "I Need a Marg",
            },
            "image_url": "https://assets3.thrillist.com/v1/image/1682388/size/tl-horizontal_main.jpg",
            "alt_text": "marg"
        }
    ]