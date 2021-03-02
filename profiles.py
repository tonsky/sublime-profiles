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

def previous_profile():
    if os.path.exists(previous_profile_path):
        with open(previous_profile_path) as file:
            return file.read().strip()
    else:
        return None

def profile_path(name):
    return os.path.join(base_path, name + '.profile')

def profiles():
    items = {current_profile()}
    for path in os.listdir(base_path):
        if path.endswith('.profile'):
            items.add(path[:-len('.profile')])
    return sorted(items)


# Create

class ProfileNameInputHandler(sublime_plugin.TextInputHandler):
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
    def run(self, profile_name):
        os.makedirs(base_path, exist_ok=True)

        # Save current
        shutil.copyfile(preferences_path, profile_path(current_profile()))

        # Save old current to previous
        with open(previous_profile_path, "w") as file:
          file.write(current_profile())

        # Save new current name
        with open(current_profile_path, "w") as file:
          file.write(profile_name)

    def input(self, args):
        return ProfileNameInputHandler()


# Switch

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
        switch_profile_path = profile_path(switch_profile)
        shutil.copyfile(switch_profile_path, preferences_path)

        # Remove old copy of new current
        os.remove(switch_profile_path)

    def input(self, args):
        return SwitchProfileInputHandler()

    def is_enabled(self):
        return len(profiles()) > 1

# Rename

class RenameProfileInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        self.profiles = profiles()
        self.current_profile = current_profile()

    def placeholder(self):
        return 'Select profile'

    def list_items(self):
        return [("→ " + x if x == self.current_profile else x) for x in self.profiles if x != "Default"]

    def next_input(self, args):
        return ProfileNameInputHandler()

class RenameProfileCommand(sublime_plugin.ApplicationCommand):
    def run(self, rename_profile, profile_name):
        rename_profile = rename_profile.strip("→ ")
        if rename_profile == current_profile():
            with open(current_profile_path, "w") as file:
                file.write(profile_name)
        else:
            os.rename(profile_path(rename_profile), profile_path(profile_name))
            if previous_profile() == rename_profile:
                with open(previous_profile_path, "w") as file:
                    file.write(profile_name)

    def input(self, args):
        return RenameProfileInputHandler()

    def is_enabled(self):
        return len(profiles()) > 1


# Delete

class DeleteProfileInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        self.profiles = profiles()
        self.current_profile = current_profile()

    def placeholder(self):
        return 'Select profile'

    def list_items(self):
        return ["× " + x for x in self.profiles if x != "Default" and x != self.current_profile]

class DeleteProfileCommand(sublime_plugin.ApplicationCommand):
    def run(self, delete_profile):
        delete_profile = delete_profile[len("× "):]
        os.remove(profile_path(delete_profile))
        if (previous_profile() == delete_profile):
            os.remove(previous_profile_path)

    def input(self, args):
        return DeleteProfileInputHandler()

    def is_enabled(self):
        return len(profiles()) > (1 if current_profile() == "Default" else 2)


# Toggle

class ToggleProfileCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        p = previous_profile()
        if p:
            SwitchProfileCommand().run(p)

    def is_enabled(self):
        return os.path.exists(previous_profile_path)