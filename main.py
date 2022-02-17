

import sys
import cartiv
import time

"""
TODO
    - Add primitive UI so we can register just to test this stuff out
        Should be able to sign in, and after that change... 
            - display name
            - the group you belong to (ie. group id)
            - add other users to your group
            - add items to your group's shopping list
            - define custom shopping items
    - Figure out how to generate tokens and make sure the user passes them in the request header so we can identify them
        (eg. after user logs in, we generate some sort of string that users will attach to their GET requests so we can identify them)
        (need to make sure this expires after like 24hrs or smthn. should probs google it!)
    - Figure out how to store shopping list per group (eg. 1 table per group or one macro table with a string field that contains json strings???)
    - Create table for custom shopping items 
"""

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print("Please pass in a config filepath!")
        exit()

    c = cartiv.Cartiv(sys.argv[1])
    c.run()
    time.sleep(10000)

