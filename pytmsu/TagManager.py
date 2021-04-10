from . import speller
import subprocess


class TagManager():
    def __init__(self, tm):
        self.tags_to_add = []
        self.tags_to_remove = []
        self.all_tags_added = set()
        self.tags_assorted = set()
        self.tm = tm
        self.all_tagnames = set()
        self.all_tagnames = {tag.name for tag in self.tm.get_tags()}

    def parse_user_tags(self, user_input):
        self.tags_to_add = []
        self.tags_to_remove = []
        tags = user_input.split(",")
        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue
            if tag.startswith("-"):
                new_tag = tag[1::]
                self.tags_to_remove.append(new_tag)
                if new_tag in self.all_tags_added:
                    self.all_tags_added.remove(new_tag)
            else:
                self.tags_to_add.append(tag)
                self.all_tags_added.add(tag)
        return self.tags_to_add, self.tags_to_remove

    def next_image(self):
        self.tags_to_add = []
        self.tags_to_remove = []
        self.tags_assorted = self.all_tags_added
        self.all_tags_added = set()
        self.all_tagnames = {tag.name for tag in self.tm.get_tags()}

    def manage(self, filepath, user_input):
        self.parse_user_tags(user_input)
        self.add_tags(filepath)
        self.remove_tags(filepath)

    def add_tags(self, filepath):
        """
        Method that adds {tags} to file
        """
        if not self.tags_to_add:
            return

        for tag in self.tags_to_add:
            suggestion = speller.spellcheck(tag, self.all_tagnames)
            if suggestion:
                prompt = f"""Did you mean the following tag? {suggestion}
                        y/N
                        """
                answer = input(prompt)
                if answer in ['yes', 'y']:
                    self.tags_to_add.remove(tag)
                    tag = suggestion
                    self.tags_to_add.append(tag)
            subprocess.run(
                ['tmsu', 'tag', filepath, tag],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        print(f"Added tags {' '.join(self.tags_to_add)} to file {filepath}")
        for tag in self.tags_to_add:
            if "edit-date" not in tag:
                self.tags_assorted.add(tag)

        self.tags_to_add = []

    def remove_tags(self, filepath: str):
        if self.tags_to_remove:
            for tag in self.tags_to_remove:
                subprocess.run(
                    ['tmsu', 'untag', filepath, tag],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            print(f"Removed tags {' '.join(self.tags_to_remove)} from file {filepath}")

        self.tags_to_remove = []
