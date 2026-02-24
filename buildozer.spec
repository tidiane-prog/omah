[app]

# Titre de l'application
title = Elite Neural Evolve

# Nom du package
package.name = eliteneural

# Domaine du package
package.domain = ai.elite

# Dossier source
source.dir = .

# Extensions à inclure
source.include_exts = py,png,jpg,kv,json,txt

# Version
version = 8.0.0

# Requirements (dépendances)
requirements = python3,kivy,numpy

# Icône
icon.filename = assets/icon.png

# Splash screen
presplash.filename = assets/splash.png

# Orientation
orientation = portrait

# Plein écran
fullscreen = 0

# Permissions Android
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET,VIBRATE

# API Android cible
android.api = 33

# API minimum
android.minapi = 21

# NDK
android.ndk = 25b

# Accepter la licence SDK
android.accept_sdk_license = True

# Architectures
android.archs = arm64-v8a, armeabi-v7a

# Backup Android
android.allow_backup = True

# SDK Target
android.sdk_target = 33

# Branch p4a
p4a.branch = master

# Dépendances Gradle
android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1

# Copier les libs
android.copy_libs = 1

[buildozer]

# Niveau de log
log_level = 2

# Dossier de build
build_dir = ./.buildozer

# Dossier de sortie
bin_dir = ./bin
