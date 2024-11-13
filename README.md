# Calendar Redacter

If you have some calendar(s) on a calendar service that supports
CalDAV (e.g. Fastmail, Google Calendar) then this is a Python script
that can create a copy of those calendar(s) with all the details
redacted, and save it back to the same service. It's like the
free/busy sharing feature. Except, I found that sometimes the
implementation of that feature does not work well, e.g. recurring
events are unrolled into every individual repetition of the event,
bloating the size of the shared calendar massively. The implementation
in this script is very simple, it just combines all the events from
the selected calendar(s) and deletes/redacts the properties that have
identifying information, but leaves other fields such as repeating
rules the same.

## Usage

Clone the repo and create `.env` file in it

```
CALDAV_URL=
CALDAV_USERNAME=
CALDAV_PASSWORD=
CALDAV_COLLECTIONS=
CALDAV_REDACTED=
```

The URL, username, and password are your CalDAV connection details.

* Fastmail is straightforward:
  [documentation](https://www.fastmail.help/hc/en-us/articles/1500000278342-Server-names-and-ports#calendar)
* Google has something with OAuth2...? You can try figuring it out if
  you want.

The last two parameters are your calendar/collection IDs to operate
on. First one is a list of the calendars to combine (comma-separated
list), second one is the calendar to write the redacted events to. You
identify calendars using their CalDAV IDs, not using their display
names. On Fastmail for example, these are UUIDs and you can find them
by clicking "export" next to a calendar in the settings and noting the
UUID in the URL.

Install dependencies with [Poetry](https://python-poetry.org/) or
equivalent following the versions in `pyproject.toml`, `poetry.lock`.
Execute

```
poetry run python -m calendar_redacter
```

on a cron job with the desired frequency. Your events should show up
automatically in the target calendar you specified.

## More details?

I wrote this documentation in 5 minutes. If something is unclear just
ask and I will add more details to cover the issue.
