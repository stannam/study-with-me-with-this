#!/bin/sh
# run this shell script AFTER CREATING an .app file to create a DMG distribution of the executable on a mac.

# Create a folder 'dmg' under dist and use it to prepare the DMG.
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/Study with This.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/Study with This.dmg" && rm "dist/Study with This.dmg"

create-dmg \
  --volname "Study with me with this" \
  --volicon "icons/icon.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "Study with This.app" 175 120 \
  --hide-extension "Study with This.app" \
  --app-drop-link 425 120 \
  "dist/Study with This.dmg" \
  "dist/dmg/"
  