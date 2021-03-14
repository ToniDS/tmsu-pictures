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

    def add_tags(self, filepath, tags_assorted = None, all_tagnames = None):
        """
        Method that adds {tags} to file
        """
        if tags_assorted is None: 
            tags_assorted = []
        if all_tagnames is None:
            all_tagnames = set()
        #Option
        if not tags: 
            return
        for tag in tags:
            suggestion = speller.spellcheck(tag, all_tagnames)
            if suggestion:
                prompt = f"""Did you mean the following tag? {suggestion}
                        y/N
                        """
                answer = input(prompt)
                if answer in ['yes', 'y']:
                    tags.remove(tag)
                    tag = suggestion
                    tags.append(tag)
            subprocess.Popen(['tmsu', 'tag', filepath, tag],
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        print(f"Added tags {' '.join(tags)} to file {filepath}")
        for tag in tags: 
            if "edit-date" not in tag:
                tags_assorted.append(tag)


    def remove_tags(tags_to_remove: list, filepath: str):
        if tags_to_remove:
            for tag in tags_to_remove:
                subprocess.Popen(['tmsu', 'untag', filepath, tag],
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            print(f"Removed tags {' '.join(tags_to_remove)} from file {filepath}")
