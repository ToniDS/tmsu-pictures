import subprocess
import readline


def clean_name(some_var):
    """ Helper function to make variables usable in SQLite queries
    without risk of SQL injection vulnerability."""
    var = str(some_var)
    return ''.join(char for char in var if char.isalnum())


def parse_user_tags(input):
    tags = input.split(",")
    tags_to_remove = []
    tags_to_add = []
    for tag in tags:
        tag = tag.strip()
        if tag[0] == "-":
            new_tag = tag[1::]
            tags_to_remove.append(new_tag)
        else:
            tags_to_add.append(tag)
    return tags_to_add, tags_to_remove


def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def clean_up(db_connection, feh_process):
    """Check if there's tags without a file associated to them, then remove
    them from the database."""
    tags_to_delete = []
    for tag in db_connection.get_tags():
        if len(db_connection.get_files_for_tag(tag)) == 0:
            tags_to_delete.append(tag.name)
    db_connection.close()
    if len(tags_to_delete) >= 1:
        for tag in tags_to_delete:
            subprocess.Popen(['tmsu', 'delete', tag])
    feh_process.kill()
