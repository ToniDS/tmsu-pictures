class ProcessedInput():
    STATE_NOT_SET = -1
    STATE_NEXT_IMAGE = 0
    STATE_LIST_TAGS = 1
    STATE_MODIFY_TAGS = 2
    STATE_EXIT = 3

    def __init__(self):
        self.state = ProcessedInput.STATE_NOT_SET
        self.user_input = None
