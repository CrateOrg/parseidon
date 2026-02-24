import pluggy

hookspec = pluggy.HookspecMarker(project_name="parseidon")


class ContentHandlerSpecs:

    @hookspec
    def post_process_content(self, output, trie_file):
        """Post process content"""
