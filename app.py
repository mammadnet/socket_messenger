def add_message(message):
    # Check if message already exists
    if message.get("id") not in message_ids:
        messages.append(message)
        message_ids.add(message.get("id"))
        print(f"Added message: {message.get('id')}")
    else:
        # If the message already exists and was sent by the user, don't add it again
        # This prevents duplicate messages when the server sends back the same message
        if message.get("sent_by_user"):
            print(f"Skipping duplicate user-sent message: {message.get('id')}")
            return
        else:
            print(f"Message already exists: {message.get('id')}") 