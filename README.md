# KDE Auto Day/Night Mode
A simple Python script for selecting and automatic switching of day and night theme for KDE Plasma.

## Requirements
- Install `geoclue2` package.
	- ArchLinux: `pacman -S geoclue`
	- CentOS: `sudo dnf -y install geoclue2` or `sudo yum -y install geoclue2`
	- Debian: `sudo apt-get install geoclue-2.0`
- Make sure you have Python3 (usually comes by default with major distributions).


## Install and Run Automatically
Use the commands below to install as a Systemd service and a timer. You will be prompted to select a day theme and a night theme. If you need to set any extra options, read the [Running Manually](#running-manually) section.

```bash
./configure && make install
```

You can now verify the installation was successful using:
```bash
systemctl --user list-timers

# NEXT                          LEFT LAST                              PASSED UNIT                          ACTIVATES
# Wed 2023-11-15 09:24:12 EET   6min Wed 2023-11-15 09:14:12 EET 3min 26s ago kde-auto-day-night-mode.timer kde-auto-day-night-mode.service

systemctl --user status kde-auto-day-night-mode.service

# ○ kde-auto-day-night-mode.service - Automatic day/night mode switcher
#      Loaded: loaded (/home/dir/.config/systemd/user/kde-auto-day-night-mode.service; enabled; preset: enabled)
#      Active: inactive (dead) since Wed 2023-11-15 09:14:17 EET; 3min 24s ago
#    Duration: 5.767s
# TriggeredBy: ● kde-auto-day-night-mode.timer
#     Process: 4605 ExecStart=python /usr/local/bin/kde-auto-day-night-mode.py -d org.kde.breeze.desktop -n org.kde.breezedark.desktop (code=exited, status=0/SUCCESS)
#    Main PID: 4605 (code=exited, status=0/SUCCESS)
#         CPU: 50ms

# Nov 15 09:14:12 system-name systemd[1136]: Started Automatic day/night mode switcher.
```

"Active: inactive (dead)" is OK. The script runs quickly then exits to save system resources. However, if it says "failed", then it is not working properly.

### As a Cronjob
If you don't like or can not use Systemd timers, set up a cronjob:
```bash
*/10 * * * * python kde-auto-day-night-mode.py -d DAY_THEME_NAME -n NIGHT_THEME_NAME
```

## Run Manually
If you would like to run the script manually or you need more configuration options in automatic mode, read the instructions below. Otherwise, you may skip this section.

Get the list of all themes on your system:
```bash
lookandfeeltool -l

# Example list:
# org.kde.breezedark.desktop
# com.endeavouros.breezedarkeos.desktop
# org.kde.breezetwilight.desktop
# org.kde.breeze.desktop
```

Pick day and night themes from the list and run the Python script. It will detect your location, check the current time and switch to the appropriate theme.
```bash
python kde-auto-day-night-mode.py -d org.kde.breeze.desktop -n org.kde.breezedark.desktop
```

### where-am-i
In some distributions the geolocation tool may not be at the default path: `/usr/lib/geoclue-2.0/demos/where-am-i`. You can select a different path with the `-w` command-line argument:
```bash
python kde-auto-day-night-mode.py -w /some/other/path/where-am-i -d DAY_THEME -n NIGHT_THEME
```

### Geolocation cache
By default the current geolocation will be stored in: `~/.cache/kde-auto-day-night-geolocation`. However, if your distribution is not meant to have a `.cache` directory in HOME, you can select a different path for the geolocation cache file:
```bash
python kde-auto-day-night-mode.py -f /new/path/for/the-cache-file -d DAY_THEME -n NIGHT_THEME
```

_Tip: If your location seems to be incorrect, you can force redetection using the `-l` command-line argument. Alternatively, you can delete the cache file. This will automatically trigger redetection._

### Other Options
The full list of options can be viewed with `-h`:
```bash
python kde-auto-day-night-mode.py -h
```
