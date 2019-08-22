import csv
import StringIO
import uuid

from django.contrib.auth.models import User

from guests.models import Party, Guest


def import_guests(path):
    with open(path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                continue
            party_name, first_name, last_name, party_type, is_child, category, is_invited, email = row[:8]
            if not party_name:
                print 'skipping row {}'.format(row)
                continue
            party = Party.objects.get_or_create(name=party_name)[0]
            party.type = party_type
            party.category = category
            party.is_invited = _is_true(is_invited)
            if not party.invitation_id:
                party.invitation_id = uuid.uuid4().hex
            party.save()

            user = User.objects.filter(username=str(party.id)).first()

            if not user:
                user = User.objects.create_user(
                    username=str(party.id),
                    email=email,
                    password=party.invitation_id
                )

                party.user_id = user.id
                party.save(update_fields=['user_id'])

            if email:
                guest, created = Guest.objects.get_or_create(party=party, email=email)
                guest.first_name = first_name
                guest.last_name = last_name
            else:
                guest = Guest.objects.get_or_create(party=party, first_name=first_name, last_name=last_name)[0]
            guest.is_child = _is_true(is_child)
            guest.save()


def export_guests():
    headers = [
        'party_name', 'first_name', 'last_name', 'party_type',
        'is_child', 'category', 'is_invited', 'is_attending',
        'rehearsal_dinner', 'meal', 'email', 'comments'
    ]
    file = StringIO.StringIO()
    writer = csv.writer(file)
    writer.writerow(headers)
    for party in Party.in_default_order():
        for guest in party.guest_set.all():
            if guest.is_attending:
                writer.writerow([
                    party.name,
                    guest.first_name,
                    guest.last_name,
                    party.type,
                    guest.is_child,
                    party.category,
                    party.is_invited,
                    guest.is_attending,
                    party.rehearsal_dinner,
                    guest.meal,
                    guest.email,
                    party.comments,
                ])
    return file


def _is_true(value):
    value = value or ''
    return value.lower() in ('y', 'yes')
