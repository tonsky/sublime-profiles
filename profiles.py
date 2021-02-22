import os, re, shutil, sublime, sublime_plugin

package_name = 'sublime-profiles'
base_path = os.path.join(sublime.packages_path(), package_name, 'Data')
current_profile_path = os.path.join(base_path, 'current')
previous_profile_path = os.path.join(base_path, 'previous')
preferences_path = os.path.join(sublime.packages_path(), 'User', 'Preferences.sublime-settings')

def current_profile():
    if os.path.exists(current_profile_path):
        with open(current_profile_path) as file:
            return file.read().strip()
    else:
        return 'Default'

def profiles():
    items = {current_profile()}
    for path in os.listdir(base_path):
        if path.endswith('.profile'):
            items.add(path[:-len('.profile')])
    return sorted(items)

class CreateProfileInputHandler(sublime_plugin.TextInputHandler):
    def placeholder(self):
        return "Profile name"

    def preview(self, text):
        text = text.strip()
        if text.lower() in [p.lower() for p in profiles()]:
            return "'" + text + "' already exists"

    def validate(self, text):
        text = text.strip().lower()
        return bool(text and text not in [p.lower() for p in profiles()])

class CreateProfileCommand(sublime_plugin.ApplicationCommand):
    def run(self, create_profile):
        os.makedirs(base_path, exist_ok=True)

        # Save current
        shutil.copyfile(preferences_path, os.path.join(base_path, current_profile() + ".profile"))

        # Save old current to previous
        with open(previous_profile_path, "w") as file:
          file.write(current_profile())

        # Save new current name
        with open(current_profile_path, "w") as file:
          file.write(create_profile)

    def input(self, args):
        return CreateProfileInputHandler()

class SwitchProfileInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        self.profiles = profiles()
        self.current_profile = current_profile()

    def placeholder(self):
        return 'Select profile'

    def list_items(self):
        return [("→ " + x if x == self.current_profile else x) for x in self.profiles]

    def validate(self, value):
        return not value.startswith("→ ")

class SwitchProfileCommand(sublime_plugin.ApplicationCommand):
    def run(self, switch_profile):
        CreateProfileCommand().run(switch_profile)

        # Load target profile
        switch_profile = switch_profile.strip("→ ")
        switch_profile_path = os.path.join(base_path, switch_profile + '.profile')
        shutil.copyfile(switch_profile_path, preferences_path)

        # Remove old copy of new current
        os.remove(switch_profile_path)

    def input(self, args):
        return SwitchProfileInputHandler()

    def is_enabled(self):
        return len(profiles()) > 1

class ToggleProfileCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        if os.path.exists(previous_profile_path):
            with open(previous_profile_path) as file:
                previous_profile = file.read().strip()
            SwitchProfileCommand().run(previous_profile)

    def is_enabled(self):
        return os.path.exists(previous_profile_path)