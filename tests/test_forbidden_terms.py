import unittest

from tools.validate_skills import contains_forbidden_term


class ForbiddenTermTests(unittest.TestCase):
    def test_short_term_does_not_match_inside_a_word(self):
        self.assertFalse(contains_forbidden_term("Omitting the list is not an empty trace.", "pty"))
        self.assertFalse(contains_forbidden_term("empty", "pty"))

    def test_term_matches_as_its_own_word(self):
        self.assertTrue(contains_forbidden_term("Do not target a pty device.", "pty"))
        self.assertTrue(contains_forbidden_term("Open a GitHub issue for this.", "github issue"))

    def test_phrase_does_not_match_a_longer_token(self):
        self.assertFalse(contains_forbidden_term("macosx build", "macos"))


if __name__ == "__main__":
    unittest.main()
