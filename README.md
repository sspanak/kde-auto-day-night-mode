# linux-auto-day-night-mode
A simple to use Python script for auto-switching between day and night themes. Currently supports only KDE Plasma.

## Installation
- Install `geoclue2` package.
	- ArchLinux: `pacman -S geoclue`
	- CentOS: `sudo dnf -y install geoclue2` or `sudo yum -y install geoclue2`
	- Debian: `sudo apt-get install geoclue-2.0`
- Make sure you have Python3 (usually comes by default with major distributions).
- Download the `.py` file and put it anywhere you like. For example: `~/scripts/linux-auto-day-night-mode.py`.
- Make it executable `chmod +x ~/scripts/linux-auto-day-night-mode.py`
- Set it up to run every 10 minutes or so. See [Usage](#usage) below.

## Usage

Get the list of all themes on your system:
```bash
lookandfeeltool -l

# Example list:
# org.kde.breezedark.desktop
# com.endeavouros.breezedarkeos.desktop
# org.kde.breezetwilight.desktop
# org.kde.breeze.desktop
```

Pick day and night themes from the list and run the Python script. It will detect your location, check the current time and switch to the appropriate time.
```bash
python linux-auto-day-night-mode.py -d org.kde.breeze.desktop -n org.kde.breezedark.desktop
```

### where-am-i
In some distributions the geolocation tool may not be at the default path: `/usr/lib/geoclue-2.0/demos/where-am-i`. You can select a different path with the `-w` command-line argument:
```bash
python linux-auto-day-night-mode.py -w /some/other/path/where-am-i -d DAY_THEME -n NIGHT_THEME
```

### Geolocation cache
By default the current geolocation will be stored in: `~/.cache/linux-auto-day-night-geolocation`. However, if your distribution does is not meant to have a `.cache` directory in HOME, you can select a different path for the geolocation cache file:
```bash
python linux-auto-day-night-mode.py -f /new/path/for/the-cache-file -d DAY_THEME -n NIGHT_THEME
```

If your location seems to be incorrect, you can force redetection using the `-l` command-line argument. Alternatively, you can delete the cache file. This will automatically trigger redetection.

### Other Options
The full list of options can be viewed with `-h`:
```bash
python linux-auto-day-night-mode.py -h
```
