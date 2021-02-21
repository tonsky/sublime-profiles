# Profile switcher for Sublime Text

## Installation

`Package Control: Install Package` → `Profile Switcher`.

## Usage

1. Create a  new profile via `Profiles: Create Profile` command.
2. Edit your SublimeText settings as usual.
3. Switch back to previous profile via `Profiles: Switch Profile`.

## Features 

- Each profile remembers all the settings: font, scheme, line metrics, gutter, etc.
- Any number of profiles.
- Instant switching.

## How does it work?

Profiles maintain a copy of `Preferences.sublime-settings`, one per profile.

When switching to the profile, current `Preferences.sublime-settings` is saved, and profile version is copied over current `Preferences.sublime-settings`.

Inactive profiles are stored in `~/Library/Application Support/Sublime Text/Packages/sublime-profiles`.

## License

[MIT License](./LICENSE.txt)