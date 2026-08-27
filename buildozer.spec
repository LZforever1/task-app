[app]

title = TaskApp
package.name = taskapp
package.domain = org.lzforever

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,ttc
source.include_patterns = assets/*,images/*
source.exclude_dirs = tests, bin

version = 0.1

requirements = python3,kivy,pyjnius,android

orientation = portrait
fullscreen = 0

android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk_api = 21

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

android.accept_sdk_license = True

# (str) The Android entry point
source.main = task.py

[buildozer]

log_level = 2
warn_on_root = 1