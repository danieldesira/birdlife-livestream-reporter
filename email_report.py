def load_email_template():
    try:
        with open('email_template.html') as file:
            return file.read()
    except FileNotFoundError:
        print('email_template.html not found')
