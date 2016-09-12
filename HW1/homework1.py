############################################################
# HOMEWORK 1
#
# Team members: Deniz Celik, Jacob Riedel
#
# Emails: deniz.celik@students.olin.edu
#         jacob.riedel@students.olin.edu
#
# Remarks:
#




#
# Expressions
#

class Exp (object):
    pass


class EInteger (Exp):
    # Integer literal

    def __init__ (self,i):
        self._integer = i

    def __str__ (self):
        return "EInteger({})".format(self._integer)

    def eval (self):
        return VInteger(self._integer)


class EBoolean (Exp):
    # Boolean literal

    def __init__ (self,b):
        self._boolean = b

    def __str__ (self):
        return "EBoolean({})".format(self._boolean)

    def eval (self):
        return VBoolean(self._boolean)


class EPlus (Exp):
    # Addition operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EPlus({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value + v2.value)
        raise Exception ("Runtime error: trying to add non-numbers")


class EMinus (Exp):
    # Subtraction operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EMinus({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value - v2.value)
        raise Exception ("Runtime error: trying to subtract non-numbers")


class ETimes (Exp):
    # Multiplication operation

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "ETimes({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value * v2.value)
        raise Exception ("Runtime error: trying to multiply non-numbers")


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self):
        v = self._cond.eval()
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval()
        else:
            return self._else.eval()


class EIsZero (Exp):
    # Conditional Expression

    def __init__(self,e1):
        self._val = e1

    def __str__ (self):
        return "EIsZero({})".format(self._val)

    def eval(self):
        v = self._val.eval()
        if v.type != "integer":
            raise Exception ("Runtime error: Expression is not an Integer")
        if v.value == 0:
            return VBoolean(True)
        else:
            return VBoolean(False)


class EAnd (Exp):

    def __init__(self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2


    def __str__(self):
        return "EAnd({},{})".format(self._exp1,self._exp2)

    def eval(self):
        v1 = self._exp1.eval()
        if v1.type != "boolean":
            raise Exception("Runtime error: first expression is not a boolean")
        if not v1.value:
            return VBoolean(False)

        v2 = self._exp2.eval()
        if v2.type != "boolean":
            raise Exception("Runtime error: second expression is not a boolean")
        if v2.value:
            return VBoolean(True)
        else:
            return VBoolean(False)

class EOr(Exp):

    def __init__(self, e1, e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__(self):
        return "EOr({},{})".format(self._exp1,self._exp2)
        
    def eval(self):
        v1 = self._exp1.eval()
        if v1.type != "boolean":
            raise Exception("Runtime error: first expression is not a boolean")
        if v1.value:
            return VBoolean(True)

        v2 = self._exp2.eval()
        if v2.type != "boolean":
            raise Exception("Runtime error: second expression is not a boolean")
        if not v2.value:
            return VBoolean(False)
        else:
            return VBoolean(True)

#
# Values
#

class Value (object):
    pass


class VInteger (Value):
    # Value representation of integers
    def __init__ (self,i):
        self.value = i
        self.type = "integer"

class VBoolean (Value):
    # Value representation of Booleans
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"


if __name__ == '__main__':
    print "EIsZero Tester >>"
    print "Expected: True  Output: " + str(EIsZero(EInteger(0)).eval().value)
    print "Expected: False  Output: " + str(EIsZero(EInteger(1)).eval().value)
    print "Expected: False  Output: " + str(EIsZero(EInteger(9)).eval().value)
    print "Expected: False  Output: " + str(EIsZero(EInteger(-1)).eval().value)
    print "Expected: False  Output: " + str(EIsZero(EPlus(EInteger(1),EInteger(1))).eval().value)
    print "Expected: True  Output: " + str(EIsZero(EMinus(EInteger(1),EInteger(1))).eval().value)

    tt = EBoolean(True)
    ff = EBoolean(False)
    print "EAnd Tester >>"
    print "Expected: True Output: " + str(EAnd(tt,tt).eval().value)
    print "Expected: False Output: " + str(EAnd(tt,ff).eval().value)
    print "Expected: False Output: " + str(EAnd(ff,tt).eval().value)
    print "Expected: False Output: " + str(EAnd(ff,ff).eval().value)
    print "Expected: False Output: " + str(EAnd(ff,EInteger(10)).eval().value)
    print "Expected: False Output: " + str(EAnd(ff,EInteger(0)).eval().value)

    print "EOr Tester >>"
    print "Expected: True Output: " + str(EOr(tt,tt).eval().value)
    print "Expected: True Output: " + str(EOr(tt,ff).eval().value)
    print "Expected: True Output: " + str(EOr(ff,tt).eval().value)
    print "Expected: False Output: " + str(EOr(ff,ff).eval().value)
    print "Expected: True Output: " + str(EOr(tt,EInteger(10)).eval().value)
    print "Expected: True Output: " + str(EOr(tt,EInteger(0)).eval().value)

    print "ENot Tester >>"
    print "Expected: False Output: " + str(ENot(tt).eval().value)
    print "Expected: True Output: " + str(ENot(ff).eval().value)

    print "EAnd, EOr, ENot Tester >>"
    print "Expected: True Output: " + str(EAnd(EOr(tt,ff),EOr(ff,tt)).eval().value)
    print "Expected: False Output: " + str(EAnd(EOr(tt,ff),EOr(ff,ff)).eval().value)
    print "Expected: False Output: " + str(EAnd(tt,ENot(tt)).eval().value)
    print "Expected: True Output: " + str(EAnd(tt,ENot(ENot(tt))).eval().value)

