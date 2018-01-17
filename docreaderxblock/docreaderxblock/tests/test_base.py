import unittest
import copy

class TestBase(unittest.TestCase):

    def runtest(self, defaultPara = None):
        self.set_up()
        list_of_attrs = list(self.__class__.__dict__)
        for each_attr in list_of_attrs:
            if "test_" in each_attr:
                try:
                    getattr(self, each_attr)()
                    print "testing {}.{} passed".format(str(self.__class__), each_attr)
                except:
                    print "testing {}.{} failed".format(str(self.__class__), each_attr)

        if defaultPara is not None:
            self.set_up(defaultPara)
            for each_attr in list_of_attrs:
                if "test_" in each_attr:
                    try:
                        getattr(self, each_attr)()
                        print "testing {}.{} passed".format(str(self.__class__), each_attr)
                    except:
                        print "testing {}.{} failed".format(str(self.__class__), each_attr)
