[app]
title = WeatherApp
package.name = weatherapp
package.domain = org.wheather
source.dir = .
source.include_exts = py, kv, png, jpg
version = 0.1
requirements = python3,kivy,requests
orientation = portrait
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
# icon.filename = icon.png

[buildozer]
log_level = 2
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
