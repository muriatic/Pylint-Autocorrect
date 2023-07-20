import re
import logging
import Lib.errors

def validate_phone_numbers(phone_numbers, names):
    corrected_phone_numbers = []
    # create phone number regex
    pattern = re.compile(r'([0-9]{1,3})?([0-9]{3})([0-9]{3})([0-9]{4})')

    for phone_number in phone_numbers:
        logging.debug(f'{phone_number=}')
        name = names[phone_numbers.index(phone_number)]

        # convert it to string
        phone_number = str(phone_number)

        digits_only_phone_number = re.sub('[^0-9]', '', phone_number)

        if len(digits_only_phone_number) < 10:
            raise Lib.errors.IncorrectPhoneNumberLength(f'phone number \'{phone_number}\' for {name} is too short and unable to be resolved')

        if len(digits_only_phone_number) > 13:
            raise Lib.errors.IncorrectPhoneNumberLength(f'phone number \'{phone_number}\' for {name} is too long and unable to be resolved')

        match = pattern.search(digits_only_phone_number)

        country_code = match.group(1)
        area_code = match.group(2)
        telephone_prefix = match.group(3)
        line_number = match.group(4)

        if country_code:
            corrected_phone_number = f'+{country_code} ({area_code}) {telephone_prefix} - {line_number}'

        else:
            corrected_phone_number = f'({area_code}) {telephone_prefix} - {line_number}'

        logging.info(f'phone number: {phone_number} was corrected to {corrected_phone_number} using RegEx')

        corrected_phone_numbers.append(corrected_phone_number)

    return corrected_phone_numbers


def validate_emails(emails, names):
    # create email regex
    pattern = re.compile(r'([A-Za-z0-9!#$%\^&*+\-_\.\"]+)\@(\[)?([A-Za-z0-9\-\.]+)\.([A-Za-z0-9]+)(\])?')

    for email in emails:
        logging.debug(f'{email=}')
        if not pattern.match(email):
            name = names[emails.index(email)]
            raise Lib.errors.InvalidEmailAddress(f'email \'{email}\' for {name} is not a valid email, ensure it follows Username@EmailServer.TLD like example@gmail.com. If this email is valid, please change the regular expression')

    return emails


def validate_linkedins(linkedins, names):
    corrected_linkedins = []

    pattern = re.compile(r'linkedin.com/in/([a-zA-z0-9\-]+)')

    for linkedin in linkedins:
        logging.debug(f'{linkedin=}')
        linkedin_lower = linkedin.lower()
        link_characters = ['/', '.', ':']

        name = names[linkedins.index(linkedin_lower)]

        if not any(substring in linkedin_lower for substring in link_characters):
            valid_linkedin = f'https://www.linkedin.com/in/{linkedin_lower}/'
            logging.warning(f'LinkedIn: \"{linkedin}\" was corrected to \"{valid_linkedin}\" assuming a handle alone was provided, please make sure that is correct.')

        elif "linkedin.com/in/" not in linkedin_lower:
            raise Lib.errors.InvalidLinkedIn(f'LinkedIn account \"{linkedin_lower}\" for {name} is invalid, please ensure it is inputted correctly')

        else:
            try:
                handle = pattern.search(linkedin_lower).group(1)
                valid_linkedin = f'https://www.linkedin.com/in/{handle}/'
                logging.info(f'LinkedIn: \"{linkedin}\" was corrected to \"{valid_linkedin}\" using RegEx.')
            except AttributeError:
                raise Lib.errors.InvalidLinkedIn(f'LinkedIn account \"{linkedin_lower}\" for {name} is missing a handle, please ensure it is inputted correctly')


        corrected_linkedins.append(valid_linkedin)

    return corrected_linkedins


def main():
    phone_numbers = ['1234567890', '(123)456-7890', '(123) 456 - 7890', '+1 123 456 7890', '+1 (123) 456 7890', '+66 (123)4567890', '11234567890']
    names = ['John', 'John', 'John', 'John', 'John', 'John', 'John']
    valid_phone_numbers = validate_phone_numbers(phone_numbers, names)
    print(valid_phone_numbers)

    emails = ['myName@mailServer.com', 'firstName.lastName@example.com', 'email@subdomain.example.com', 'firstname+lastname@example.com', 'email@123.123.123.123', 'email@[123.123.123.123]', '"email"@example.com', '1234567890@example.com', 'email@example-one.com', '_______@example.com', 'email@example.name', 'email@example.museum', 'email@example.co.jp', 'firstname-lastname@example.com']
    names = ['John', 'John', 'John', 'John', 'John', 'John', 'John', 'John', 'John', 'John', 'John', 'John', 'John', 'John']
    valid_emails = validate_emails(emails, names)
    if valid_emails != emails:
        print("Emails are NOT equal")


    linkedins = ['https://www.linkedin.com/in/first-last/', 'first-last', 'linkedin.com/in/first-last', 'www.linkedin.com/in/first-last']
    # bad_linkedins = ['linkedin/first-last', 'linkedin.com/in/']
    names = ['John', 'John', 'John', 'John', 'John']
    valid_linkedins = validate_linkedins(linkedins, names)
    print(valid_linkedins)

if __name__ == '__main__':
    main()
