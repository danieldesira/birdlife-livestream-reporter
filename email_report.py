def load_email_template():
    try:
        with open('email_template.html') as file:
            return file.read()
    except FileNotFoundError:
        print('email_template.html not found')


def generate_email_body(report_data: list):
    template = load_email_template()
    tr_markup = ''.join(map(lambda stat: f"<tr><td>{stat.name}</td><td>{stat.status}</td></tr>", report_data))
    return template.replace('<!--report-->', tr_markup)
