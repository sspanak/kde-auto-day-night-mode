#!/usr/bin/env python3

"""Adjust the KDE day/night theme.
Based on the code at: https://gist.github.com/jacopofar/ca2397944f56412e81a8882e565038af
"""
import argparse
import re
import logging
import os
from datetime import datetime, time, timezone, timedelta
from math import cos, sin, acos, asin, tan, degrees as deg, radians as rad
from time import timezone as timezone_offset


class Sun:
    """
    Calculate sunrise and sunset based on equations from NOAA
    http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html
    """

    def __init__(self, tz, lat, long):
        self.lat = lat
        self.long = long
        self.when = tz
        self.__preptime(self.when)
        self.__calc()

    def sunrise(self):
        return Sun.__timefromdecimalday(self.sunrise_t)

    def sunset(self):
        return Sun.__timefromdecimalday(self.sunset_t)

    def solarnoon(self):
        return Sun.__timefromdecimalday(self.solarnoon_t)

    def is_day(self):
        day_t = self.when.hour / 24 + self.when.minute / 24 / 60 + self.when.second / 24 / 3600

        return day_t > self.sunrise_t and day_t < self.sunset_t

    @staticmethod
    def __timefromdecimalday(day):
        """
        converts a decimal day to 24-hour format and returns it as a datetime.time object.
        """
        hours = 24.0 * day
        h = int(hours)
        minutes = (hours - h) * 60
        m = int(minutes)
        seconds = (minutes - m) * 60
        s = int(seconds)
        return time(hour=h, minute=m, second=s)

    def __preptime(self, when):
        """
        Extract information in a suitable format from when,
        a datetime.datetime object.
        """
        # datetime days are numbered in the Gregorian calendar
        # while the calculations from NOAA are distibuted as
        # OpenOffice spreadsheets with days numbered from
        # 1/1/1900. The difference are those numbers taken for
        # 18/12/2010
        self.day = when.toordinal() - (734124 - 40529)
        t = when.time()
        self.time = (t.hour + t.minute / 60.0 + t.second / 3600.0) / 24.0

        self.timezone = 0
        offset = when.utcoffset()
        if offset is not None:
            self.timezone = offset.seconds / 3600.0

    def __calc(self):
        """
        Perform the actual calculations for sunrise, sunset and
        a number of related quantities.

        The results are stored in the instance variables
        sunrise_t, sunset_t and solarnoon_t as a fraction of a day,
        e.g. 0 = midnight, 0.5 = noon, 0.999... = 23:59
        """
        timezone = self.timezone  # in hours, east is positive
        longitude = self.long     # in decimal degrees, east is positive
        latitude = self.lat      # in decimal degrees, north is positive

        time = self.time  # percentage past midnight, i.e. noon  is 0.5
        day = self.day     # daynumber 1=1/1/1900

        Jday = day + 2415018.5 + time - timezone / 24  # Julian day
        Jcent = (Jday - 2451545) / 36525    # Julian century

        Manom = 357.52911 + Jcent * (35999.05029 - 0.0001537 * Jcent)
        Mlong = 280.46646 + Jcent * (36000.76983 + Jcent * 0.0003032) % 360
        Eccent = 0.016708634 - Jcent * (0.000042037 + 0.0001537 * Jcent)
        Mobliq = 23 + (26 + ((21.448 - Jcent * (46.815 + Jcent * \
                       (0.00059 - Jcent * 0.001813)))) / 60) / 60
        obliq = Mobliq + 0.00256 * cos(rad(125.04 - 1934.136 * Jcent))
        vary = tan(rad(obliq / 2)) * tan(rad(obliq / 2))
        Seqcent = sin(rad(Manom)) * (1.914602 - Jcent * (0.004817 + 0.000014 * Jcent)) + \
            sin(rad(2 * Manom)) * (0.019993 - 0.000101 * Jcent) + sin(rad(3 * Manom)) * 0.000289
        Struelong = Mlong + Seqcent
        Sapplong = Struelong - 0.00569 - 0.00478 * \
            sin(rad(125.04 - 1934.136 * Jcent))
        declination = deg(asin(sin(rad(obliq)) * sin(rad(Sapplong))))

        eqtime = 4 * deg(vary * sin(2 * rad(Mlong)) - 2 * Eccent * sin(rad(Manom)) + 4 * Eccent * vary * sin(rad(Manom))
                         * cos(2 * rad(Mlong)) - 0.5 * vary * vary * sin(4 * rad(Mlong)) - 1.25 * Eccent * Eccent * sin(2 * rad(Manom)))

        hourangle = deg(acos(cos(rad(90.833)) /
                             (cos(rad(latitude)) *
                              cos(rad(declination))) -
                             tan(rad(latitude)) *
                             tan(rad(declination))))

        self.solarnoon_t = (
            720 - 4 * longitude - eqtime + timezone * 60) / 1440
        self.sunrise_t = self.solarnoon_t - hourangle * 4 / 1440
        self.sunset_t = self.solarnoon_t + hourangle * 4 / 1440


class Location:
    def __init__(self, timeout, force_detect, location_cache_file, where_am_i):
        self.__force_detect = force_detect
        self.__location_file = location_cache_file
        self.__timeout = timeout
        self.__where_am_i = where_am_i

        self.latitude = 0
        self.longitude = 0
        self._get_location()

    def get_local_time(self):
        hours = -timezone_offset / 60 / 60
        return datetime.now(tz=timezone(timedelta(hours=hours)))

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def _get_location(self):
        if not os.path.exists(self.__location_file) or self.__force_detect:
            os.system(
                '%s -t %d -a 4 > %s'
                % (self.__where_am_i, self.__timeout, self.__location_file))

        with open(self.__location_file) as f:
            for line in f:
                if "Latitude" in line:
                    self.latitude = float(re.sub('[a-zA-Z :°\n\r]', '', line).replace(',', '.'))

                if "Longitude" in line:
                    self.longitude = float(re.sub('[a-zA-Z :°\n\r]', '', line).replace(',', '.'))


class Theme:
    def __init__(self, day_theme, night_theme, debug):
        self.__debug = debug
        self.__day_theme = day_theme
        self.__night_theme = night_theme

    def auto_select_kde_theme(self, is_day):
        if is_day:
            new_theme = day_theme
        else:
            new_theme = night_theme

        if new_theme == '' or new_theme == None:
            if self.__debug:
                print('No theme given. Nothing to do.')
        elif new_theme != self.__get_current_kde_theme():
            if self.__debug:
                print('Switching theme to: "%s"' % new_theme)
            os.system('lookandfeeltool -a %s' % new_theme)
        elif self.__debug:
            print('Current theme is already "%s". Nothing to do.' % new_theme)

        return new_theme

    def __get_current_kde_theme(self):
        return os \
            .popen('cat ~/.config/kdeglobals | grep LookAndFeelPackage') \
            .read() \
            .replace('LookAndFeelPackage=', '') \
            .replace(' ', '') \
            .replace('\n', '')


def get_command_line_args():
    parser = argparse.ArgumentParser(
        description="Automatically switches day and night themes based on the current time of day.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-d', '--day-theme', type=str, help='set a day theme')
    parser.add_argument('-n', '--night-theme', type=str, help='set a night theme')
    parser.add_argument('-l', '--location-redetect', action='store_true', help='discards the previously saved location and attempts detection again')
    parser.add_argument('-v', '--verbose', action='store_true', help='print location and sun event times')
    parser.add_argument(
        '-f',
        '--location-cache-file',
        type=str,
        default=os.path.join(os.path.expanduser('~'), '.cache', os.path.basename(__file__).replace(".py", "")),
        help='set custom path of the where-am-i script'
    )
    parser.add_argument(
        '-w',
        '--where-am-i',
        type=str,
        default='/usr/lib/geoclue-2.0/demos/where-am-i',
        help='set custom path of the where-am-i script'
    )

    return vars(parser.parse_args())


if __name__ == "__main__":
    argv = get_command_line_args()
    debug = argv.get('verbose')
    day_theme = argv.get('day_theme', '')
    force_detect_location = argv.get('location_redetect')
    night_theme = argv.get('night_theme', '')
    location_cache_file = argv.get('location_cache_file')
    where_am_i = argv.get('where_am_i')

    location = Location(5, force_detect_location, location_cache_file, where_am_i)
    sun = Sun(location.get_local_time(), location.get_latitude(), long=location.get_longitude())
    theme = Theme(day_theme, night_theme, debug).auto_select_kde_theme(sun.is_day())

    if debug:
        print('location: %f, %f' % (location.get_latitude(), location.get_longitude()))
        print('current time:', datetime.today())
        print('sunrise:', sun.sunrise())
        print('solar noon:', sun.solarnoon())
        print('sunset:', sun.sunset())
