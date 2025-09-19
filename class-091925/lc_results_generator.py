## CREATES RESULTS ON RANDOM BASIS 

import random
from pprint import pprint

leaving_cert_results = {

    "personal_details" : {
        "NAME" : "",
        "EXAM_ID" : "",
        "IS_EXEMPT" : ""
    },

    "grades" : [], # ID, SBJ_NAME, LEVEL, GRADE

    "_debug" : {
        "GRADE_LEVEL" : {
            "H1" : [90, 100],
            "H2" : [80, 89],
            "H3" : [70, 79],
            "H4" : [60, 69],
            "H5" : [50, 59],
            "H6" : [40, 49],
            "H7" : [30, 39],
            "H8" : [0, 29]
        },
        "NAME" : {
            "FIRST" : [
                "ADAM",
                "SEAN",
                "JACK",
                "DAVID",
                "BRIAN",
                "TOM",
                "KILLIAN",
                "CONOR",
                "PAUL",
                "SHANE"
            ],
            "LAST" : [
                "WALSH",
                "MAGEE",
                "OBI",
                "GAHAN",
                "RYAN",
                "FITZPATRICK",
                "O'BRIEN",
                "THOMPSON",
                "BELL"
            ]
        }
    }
}

class Solution:
    def __init__(self, lc_table):
        self.lc_table = lc_table

        self._logic()

    def _logic(self):
        self.generateName()
        self.generateEid()
        self.generateExempt()

        pprint(self.lc_table)

    def generateName(self):
        firstNames, lastNames = self.lc_table["_debug"]["NAME"]["FIRST"], self.lc_table["_debug"]["NAME"]["LAST"]
        self.lc_table["personal_details"]["NAME"] = (firstNames[random.randint(0, (len(firstNames) - 1))] + " " + lastNames[random.randint(0, (len(lastNames) - 1))])# pprint(self.lc_table)

    def generateEid(self):
        self.lc_table["personal_details"]["EXAM_ID"] = (random.randint(1, 999999))

    def generateExempt(self):
        self.lc_table["personal_details"]["IS_EXEMPT"] = (random.randint(0, 1)) # 0 FALSE, 1 TRUE   
        



Solution(lc_table = leaving_cert_results)

