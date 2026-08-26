[app]
title = TaskApp
package.name = taskapp
package.domain = org.lzforever
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
source.main = task.py
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

# 手机屏幕尺寸适配
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.allow_backup = True