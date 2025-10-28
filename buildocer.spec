[app]
title = 4SERC Modeler
package.name = sercmodeler
package.domain = org.leszekpapiernik

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,ttf

version = 1.0
requirements = python3,kivy,numpy,matplotlib,pillow,cython

orientation = portrait

[buildozer]
log_level = 2

[app]
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

android.permissions = INTERNET

android.api = 30
android.minapi = 21
android.ndk = 19b

# Specjalne ustawienia dla matplotlib
android.add_src = 
android.add_resources = 
android.add_manifest = <uses-feature android:glEsVersion="0x00020000" android:required="true" />

p4a.branch = develop

# Optymalizacje
android.arch = armeabi-v7a
