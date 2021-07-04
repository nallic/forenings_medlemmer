import os
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from members.tests.factories import (
    MemberFactory,
)
from members.tests.test_functional.functional_helpers import log_in


"""
This tests the front page
"""


class FrontPageTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.member = MemberFactory.create()
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/activities_list_final.png")
        self.browser.quit()

    def test_front_page_as_member(self):
        # Login
        log_in(self, self.member.person)

        self.assertIn(
            "Jeres familie",
            [
                e.text
                for e in self.browser.find_elements_by_xpath(
                    "//body/descendant-or-self::*"
                )
            ],
        )
        self.browser.find_element_by_link_text("Se familie")
        self.browser.find_element_by_link_text("Afdelinger")
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Arrangementer"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Medlemskaber"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Støttemedlemskaber"),
            )
        )
        self.assertEqual(links[0], links[1])
