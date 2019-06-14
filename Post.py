class Post:
    def __init__(self):
        self.id = 0
        self.post_date = ""
        self.post_title = ""
        self.post_content = ""
        self.post_excerpt = ""
        self.meta_value = ""

    def __str__(self):
        return f"id: {self.id}\npost date: {self.post_date}\npost title: {self.post_title}\n" \
            f"post content: {self.post_content}\npost excerpt: {self.post_excerpt}\nmeta value: {self.meta_value}"
