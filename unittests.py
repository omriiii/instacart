
import sys
import cartiv
import threading


import unittest
import requests

class Test(unittest.TestCase):
    def test_index(self):
        r = requests.get("http://127.0.0.1:5000/")
        self.assertEqual(r.status_code, 200)

    def test_homepage(self):
        r = requests.get("http://127.0.0.1:5000/home")
        self.assertEqual(r.status_code, 200)

    def test_blog(self):
        r = requests.get("http://127.0.0.1:5000/blog")
        self.assertEqual(r.status_code, 200)

    def test_login(self):
        r = requests.get("http://127.0.0.1:5000/login")
        self.assertEqual(r.status_code, 200)

    def test_register(self):
        r = requests.get("http://127.0.0.1:5000/register")
        self.assertEqual(r.status_code, 200)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(Test('test_homepage'))
    return suite

def startTestThread():
    startTestsEvent.set()

def runTests(event):
    event.wait(2) # Wait for website to setup up!
    unittest.TextTestRunner().run(suite())


startTestsEvent = threading.Event()

threading.Thread(target=runTests, args=[startTestsEvent]).start()
c = cartiv.Cartiv("config.json", startTestThread)
c.run()

