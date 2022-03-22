

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
    - Need to make sure tokens expires after like 24hrs or smthn. (google lol)
    - Figure out how to store shopping list per group (eg. 1 table per group or one macro table with a string field that contains json strings???)
    - Create table for custom shopping items 
"""

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print("Please pass in a config filepath!")
        exit()

    c = cartiv.Cartiv(sys.argv[1])
    c.run()

