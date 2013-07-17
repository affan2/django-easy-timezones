django-easy-timezones
=====================

Easy timezones for Django (>=1.4) based on MaxMind GeoIP.

Quick start
-----------

0. Install django-easy-timezones

    > pip install django-easy-timezones

1. Add "easy-timezones" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'easy-timezones',
      )

2. Add EasyTimezoneMiddleware to your MIDDLEWARE_CLASSES 

    MIDDLEWARE_CLASSES = (
        ...
        'easy-timezones.middleware.EasyTimezoneMiddleware',
    )

3. Add a path to the [MaxMind GeoIP database](http://www.maxmind.com/en/geolocation_landing) in your settings file:

    GEOIP_DATABASE = '/path/to/your/geopip/database/GeoIP.dat'

4. Enable localtime in your templates.

    {% load tz %}
        The UTC time is {{ object.date }}
    {% localtime on %}
        The local time is {{ object.date }}
    {% endlocaltime %}

5. Twist one up, cause you're done, homie!