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

#The GCD function was taken from python's implementation

#The EOr and EAnd functions could be simplified while dealing
# with Vectors by recursively solving for solutions. E.g. Call
# EOr on each set of values within the vectors.

#This is a quick and dirty write up of these modules. Probably 
# many improvments exsist.

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
        if v1.type == "vector" and v2.type == "vector":
            if v1.length==v2.length:
                newvec = []
                for index in xrange(v1.length):
                    v1rat = v1.get(index)
                    v2rat = v2.get(index)
                    if v1rat.type == 'integer':
                        v1rat = VRational(v1.get(index).value,1)
                    if v2rat.type == 'integer':
                        v2rat = VRational(v2.get(index).value,1)
                    if v1rat.type == 'rational' and v2rat.type == 'rational':
                        newnum = v1rat.numer*v2rat.denom + v2rat.numer*v1rat.denom
                        newden = v1rat.denom*v2rat.denom
                        gcd_val = gcd(newnum,newden)
                        newnum = newnum/gcd_val
                        newden = newden/gcd_val
                        if newden==1:
                            newvec.append(VInteger(newnum))
                        else:
                            newvec.append(VRational(newnum, newden))
                    else:
                        raise Exception ("Runtime error: vectors cannot contain non-numbers")
                return VVector(newvec)
            else:
                raise Exception ("Runtime error: vectors must have same length")

        if v1.type == "rational" and v2.type == "rational":
            return VRational(v1.numer*v2.denom + v2.numer*v1.denom, v1.denom*v2.denom)
        if v1.type == "rational" and v2.type == "integer":
            v2 = VRational(v2.value,1)
            return VRational(v1.numer*v2.denom + v2.numer*v1.denom, v1.denom*v2.denom)
        if v1.type == "integer" and v2.type == "rational":
            v1 = VRational(v1.value,1)
            return VRational(v1.numer*v2.denom + v2.numer*v1.denom, v1.denom*v2.denom)

        if v1.type == "vector":
            newvec = []
            if v2.type == 'integer':
                v2 = VRational(v2.value,1)
            for exp in v1.vector:
                exprat = exp
                if exp.type == 'integer':
                    exprat = VRational(exp.value,1)
                if exprat.type == 'rational' and v2.type == 'rational':
                    newnum = exprat.numer*v2.denom + v2.numer*exprat.denom
                    newden = exprat.denom*v2.denom
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
                else:
                    raise Exception ("Runtime error: vectors cannot contain non-numbers")
            return VVector(newvec)

        if v2.type == "vector":
            newvec = []
            if v1.type == 'integer':
                v1 = VRational(v1.value,1)
            for exp in v2.vector:
                exprat = exp
                if exp.type == 'integer':
                    exprat = VRational(exp.value,1)
                if exprat.type == 'rational' and v1.type == 'rational':
                    newnum = v1.numer*exprat.denom + exprat.numer*v1.denom
                    newden = v1.denom*exprat.denom
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
                else:
                    raise Exception ("Runtime error: vectors cannot contain non-numbers")
            return VVector(newvec)

        raise Exception ("Runtime error: trying to add non-numbers or non-vectors")


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

        if v1.type == "vector" and v2.type == "vector":
            if v1.length==v2.length:
                newvec = []
                for index in xrange(v1.length):
                    v1rat = v1.get(index)
                    v2rat = v2.get(index)
                    if v1rat.type == 'integer':
                        v1rat = VRational(v1.get(index).value,1)
                    if v2rat.type == 'integer':
                        v2rat = VRational(v2.get(index).value,1)
                    if v1rat.type == 'rational' and v2rat.type == 'rational':
                        newnum = v1rat.numer*v2rat.denom - v2rat.numer*v1rat.denom
                        newden = v1rat.denom*v2rat.denom
                        gcd_val = gcd(newnum,newden)
                        newnum = newnum/gcd_val
                        newden = newden/gcd_val
                        if newden==1:
                            newvec.append(VInteger(newnum))
                        else:
                            newvec.append(VRational(newnum, newden))
                    else:
                        raise Exception ("Runtime error: vectors cannot contain non-numbers")
                return VVector(newvec)
            else:
                raise Exception ("Runtime error: vectors must have same length")

        if v1.type == "rational" and v2.type == "rational":
            return VRational(v1.numer*v2.denom - v2.numer*v1.denom, v1.denom*v2.denom)
        if v1.type == "rational" and v2.type == "integer":
            v2 = VRational(v2.value,1)
            return VRational(v1.numer*v2.denom - v2.numer*v1.denom, v1.denom*v2.denom)
        if v1.type == "integer" and v2.type == "rational":
            v1 = VRational(v1.value,1)
            return VRational(v1.numer*v2.denom - v2.numer*v1.denom, v1.denom*v2.denom)

        if v1.type == "vector":
            newvec = []
            if v2.type == 'integer':
                v2 = VRational(v2.value,1)
            for exp in v1.vector:
                exprat = exp
                if exp.type == 'integer':
                    exprat = VRational(exp.value,1)
                if exprat.type == 'rational' and v2.type == 'rational':
                    newnum = exprat.numer*v2.denom - v2.numer*exprat.denom
                    newden = exprat.denom*v2.denom
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
                else:
                    raise Exception ("Runtime error: vectors cannot contain non-numbers")
            return VVector(newvec)

        if v2.type == "vector":
            newvec = []
            if v1.type == 'integer':
                v1 = VRational(v1.value,1)
            for exp in v2.vector:
                exprat = exp
                if exp.type == 'integer':
                    exprat = VRational(exp.value,1)
                if exprat.type == 'rational' and v1.type == 'rational':
                    newnum = v1.numer*exprat.denom - exprat.numer*v1.denom
                    newden = v1.denom*exprat.denom
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
                else:
                    raise Exception ("Runtime error: vectors cannot contain non-numbers")
            return VVector(newvec)

        raise Exception ("Runtime error: trying to subtract non-numbers or non-vectors")


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
        if v1.type == "vector" and v2.type == "vector":
            if v1.length==v2.length:
                newsum = VRational(0,1)
                for index in xrange(v1.length):
                    v1rat = v1.get(index)
                    v2rat = v2.get(index)
                    if v1rat.type == 'integer':
                        v1rat = VRational(v1.get(index).value,1)
                    if v2rat.type == 'integer':
                        v2rat = VRational(v2.get(index).value,1)
                    if v1rat.type == 'rational' and v2rat.type == 'rational':
                        newnum = v1rat.numer*v2rat.numer
                        newden = v1rat.denom*v2rat.denom
                        gcd_val = gcd(newnum,newden)
                        newnum = newnum/gcd_val
                        newden = newden/gcd_val

                        newsum = VRational(newsum.numer*newden + newnum*newsum.denom, newsum.denom*newden)
                    else:
                        raise Exception ("Runtime error: vectors cannot contain non-numbers")
                last_gcd = gcd(newsum.numer,newsum.denom)
                last_num = newsum.numer/last_gcd
                last_den = newsum.denom/last_gcd
                if last_den == 1:
                    return VInteger(last_num)
                else:
                    return VRational(last_num,last_den)
            else:
                raise Exception ("Runtime error: vectors must have same length")
        if v1.type == "vector" and v2.type == "vector":
            if v1.length==v2.length:
                newsum = 0
                for index in xrange(v1.length):
                     if v1.get(index).type == 'integer' and v2.get(index).type == 'integer':
                         newsum += (v1.get(index).value * v2.get(index).value)
                     else:
                         raise Exception ("Runtime error: vectors cannot contain non-numbers")
                return VInteger(newsum)
            else:
                raise Exception ("Runtime error: vectors must have same length")

        if v1.type == "rational" and v2.type == "rational":
            return VRational(v1.numer*v2.numer, v1.denom*v2.denom)
        if v1.type == "rational" and v2.type == "integer":
            return VRational(v1.numer*v2.value, v1.denom)
        if v1.type == "integer" and v2.type == "rational":
            return VRational(v1.value*v2.numer, v2.denom)

        if v1.type == "vector":
            newvec = []
            if v2.type == 'integer':
                v2 = VRational(v2.value,1)
            for exp in v1.vector:
                exprat = exp
                if exp.type == 'integer':
                    exprat = VRational(exp.value,1)
                if exprat.type == 'rational' and v2.type == 'rational':
                    newnum = exprat.numer*v2.numer
                    newden = exprat.denom*v2.denom
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
                else:
                    raise Exception ("Runtime error: vectors cannot contain non-numbers")
            return VVector(newvec)

        if v2.type == "vector":
            newvec = []
            if v1.type == 'integer':
                v1 = VRational(v1.value,1)
            for exp in v2.vector:
                exprat = exp
                if exp.type == 'integer':
                    exprat = VRational(exp.value,1)
                if exprat.type == 'rational' and v1.type == 'rational':
                    newnum = exprat.numer*v1.numer
                    newden = exprat.denom*v1.denom
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
                else:
                    raise Exception ("Runtime error: vectors cannot contain non-numbers")
            return VVector(newvec)

        raise Exception ("Runtime error: trying to multiply non-numbers or non-vectors")


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
    # Conditional Expression to test if value is 0

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
    # Conditional Statement to test if Expression 1 and Expression 2 are true

    def __init__(self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2


    def __str__(self):
        return "EAnd({},{})".format(self._exp1,self._exp2)

    def eval(self):
        v1 = self._exp1.eval()
        if v1.type == "vector":
            v2 = self._exp2.eval()
            if v2.type == "vector":
                if v1.length==v2.length:
                    newvec = []
                    for index in xrange(v1.length):
                         if v1.get(index).type == 'boolean' and v2.get(index).type == 'boolean':
                             newvec.append(VBoolean(v1.get(index).value and v2.get(index).value))
                         else:
                             raise Exception ("Runtime error: vectors must contain booleans")
                    return VVector(newvec)
                else:
                    raise Exception ("Runtime error: vectors must have same length")

            if v2.type == "boolean":
                return VVector([VBoolean(exp.value and v2.value) for exp in v1.vector])

        if v1.type == "boolean":
            v2 = self._exp2.eval()
            if v2.type == "vector":
                return VVector([VBoolean(v1.value and exp.value) for exp in v2.vector])

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
    # Conditional Statement to test if Expression 1 or Expression 2 is true

    def __init__(self, e1, e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__(self):
        return "EOr({},{})".format(self._exp1,self._exp2)
        
    def eval(self):
        v1 = self._exp1.eval()
        if v1.type == "vector":
            v2 = self._exp2.eval()
            if v2.type == "vector":
                if v1.length==v2.length:
                    newvec = []
                    for index in xrange(v1.length):
                         if v1.get(index).type == 'boolean' and v2.get(index).type == 'boolean':
                             newvec.append(VBoolean(v1.get(index).value or v2.get(index).value))
                         else:
                             raise Exception ("Runtime error: vectors must contain booleans")
                    return VVector(newvec)
                else:
                    raise Exception ("Runtime error: vectors must have same length")

            if v2.type == "boolean":
                return VVector([VBoolean(exp.value or v2.value) for exp in v1.vector])

        if v1.type == "boolean":
            v2 = self._exp2.eval()
            if v2.type == "vector":
                return VVector([VBoolean(v1.value or exp.value) for exp in v2.vector])

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

class ENot(Exp):
    # Conditional Statement which switches the value given

    def __init__(self, e1):
        self._val = e1

    def __str__(self):
        return "ENot({})".format(self._val)

    def eval(self):
        v = self._val.eval()
        if v.type == "vector":
            newvector = []
            for exp in v.vector:
                if exp.type == "boolean":
                    newvector.append(VBoolean(not exp.value))
            return VVector(newvector)
        if v.type != "boolean":
            raise Exception("Runtime error: Expression is not a boolean")
        if v.value:
            return VBoolean(False)
        else:
            return VBoolean(True)

class EVector(Exp):

    def __init__(self, ve1):
        self._vector = ve1

    def __str__(self):
        return "EVector({})".format(self._vector)

    def eval(self):
        return VVector([exp.eval() for exp in self._vector])

class EDiv(Exp):
    # Statement which divides two given values
    def __init__(self, e1, e2):
        self._numexp = e1
        self._denexp = e2

    def __str__(self):
        return "EDiv({},{})".format(self._numexp,self._denexp)

    def eval(self):
        v1 = self._numexp.eval()
        v2 = self._denexp.eval()
        if v1.type == "integer":
            v1  = VRational(v1.value,1)
        if v2.type == "integer":
            v2 = VRational(v2.value,1)

        if v1.type == "vector" and v2.type == "vector":
            newvec = []
            for index in xrange(v1.length):
                v1rat = v1.get(index)
                v2rat = v2.get(index)
                if v1rat.type=='integer':
                    v1rat = VRational(v1rat.value,1)
                if v2rat.type=='integer':
                    v2rat = VRational(v2rat.value,1)
                if v1rat.type == "rational" and v2rat.type == "rational":
                    if v1rat.denom==0 or v2rat.numer==0:
                        raise Exception("Runtime Error: division by 0 is not possible")
                    newnum = v1rat.numer*v2rat.denom
                    newden = v1rat.denom*v2rat.numer
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
            return VVector(newvec)

        if v1.type == "vector":
            newvec = []
            for exp in v1.vector:
                exprat = exp
                if exp.type == 'integer':
                    exprat = VRational(exp.value,1)
                if exprat.type == 'rational' and v2.type == 'rational':
                    newnum = exprat.numer*v2.denom
                    newden = exprat.denom*v2.numer
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
                else:
                    raise Exception ("Runtime error: vectors cannot contain non-numbers")
            return VVector(newvec)

        if v2.type == "vector":
            newvec = []
            for exp in v2.vector:
                exprat = exp
                if exp.type == 'integer':
                    exprat = VRational(exp.value,1)
                if exprat.type == 'rational' and v1.type == 'rational':
                    newnum = v1.numer*exprat.denom
                    newden = v1.denom*exprat.numer
                    gcd_val = gcd(newnum,newden)
                    newnum = newnum/gcd_val
                    newden = newden/gcd_val
                    if newden==1:
                        newvec.append(VInteger(newnum))
                    else:
                        newvec.append(VRational(newnum, newden))
                else:
                    raise Exception ("Runtime error: vectors cannot contain non-numbers")
            return VVector(newvec)




        if v1.denom==0 or v2.numer==0:
            raise Exception("Runtime Error: division by 0 is not possible")
        newnum = v1.numer*v2.denom
        newden = v1.denom*v2.numer
        gcd_val = gcd(newnum,newden)
        newnum = newnum/gcd_val
        newden = newden/gcd_val
        if newden==1:
            return VInteger(newnum)
        else:
            return VRational(newnum, newden)

        if v1.type != "rational" or v2.type != "rational":
            raise Exception("Runtime Error: division not possible with non-numbers or non-vectors")
    
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

class VVector (Value):
    # Value representation of Vectors
    def __init__(self,v):
        self.vector = v
        self.length = len(v)
        self.type = "vector"

    def get(self, n):
        return self.vector[n]

class VRational (Value):
    # Value reprsentation of Rational Numbers
    def __init__(self, num, den):
        self.numer = num
        self.denom = den
        self.type = "rational"

#
# Helper Functions
#

def gcd(a,b):
        #NOTE: Taken from Python built in gcd

        # >>> from fractions import gcd
        # >>> gcd(20,8)
        # 4
        # >>> print inspect.getsource(gcd)

        """Calculate the Greatest Common Divisor of a and b.
        Unless b==0, the result will have the same sign as b (so that when
        b is divided by it, the result comes out positive).
        """
        while b:
            a, b = b, a%b
        return a

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

    print "VVector Tester >>"
    print "Expected: 0 Output: " + str(VVector([]).length)
    print "Expected: 3 Output: " + str(VVector([VInteger(10),VInteger(20),VInteger(30)]).length)
    print "Expected: 10 Output: " + str(VVector([VInteger(10),VInteger(20),VInteger(30)]).get(0).value)
    print "Expected: 20 Output: " + str(VVector([VInteger(10),VInteger(20),VInteger(30)]).get(1).value)
    print "Expected: 30 Output: " + str(VVector([VInteger(10),VInteger(20),VInteger(30)]).get(2).value)

    print "EVector Tester >>"
    print "Expected: 0 Output: " + str(EVector([]).eval().length)
    print "Expected: 3 Output: " + str(EVector([EInteger(10),EInteger(20),EInteger(30)]).eval().length)
    print "Expected: 10 Output: " + str(EVector([EInteger(10),EInteger(20),EInteger(30)]).eval().get(0).value)
    print "Expected: 20 Output: " + str(EVector([EInteger(10),EInteger(20),EInteger(30)]).eval().get(1).value)
    print "Expected: 30 Output: " + str(EVector([EInteger(10),EInteger(20),EInteger(30)]).eval().get(2).value)
    print "Expected: 2 Output: " + str(EVector([EPlus(EInteger(1),EInteger(2)),EInteger(0)]).eval().length)
    print "Expected: 3 Output: " + str(EVector([EPlus(EInteger(1),EInteger(2)),EInteger(0)]).eval().get(0).value)
    print "Expected: 0 Output: " + str(EVector([EPlus(EInteger(1),EInteger(2)),EInteger(0)]).eval().get(1).value)
    print "Expected: 2 Output: " + str(EVector([EBoolean(True),EAnd(EBoolean(True),EBoolean(False))]).eval().length)
    print "Expected: True Output: " + str(EVector([EBoolean(True),EAnd(EBoolean(True),EBoolean(False))]).eval().get(0).value)
    print "Expected: False Output: " + str(EVector([EBoolean(True),EAnd(EBoolean(True),EBoolean(False))]).eval().get(1).value)

    print "EVector Extension >>"
    def pair (v): return (v.get(0).value,v.get(1).value)

    v1 = EVector([EInteger(2),EInteger(3)])
    v2 = EVector([EInteger(33),EInteger(66)])

    print "Expected: (35,69) Output: "+ str(pair(EPlus(v1,v2).eval()))
    print "Expected: (-31,-63) Output: "+ str(pair(EMinus(v1,v2).eval()))

    b1 = EVector([EBoolean(True),EBoolean(False)])
    b2 = EVector([EBoolean(False),EBoolean(False)])

    print "Expected: (False, False) Output: "+ str(pair(EAnd(b1,b2).eval()))
    print "Expected: (True, False) Output: "+ str(pair(EOr(b1,b2).eval()))
    print "Expected: (False, True) Output: "+ str(pair(ENot(b1).eval()))

    v1 = EVector([EInteger(2),EInteger(3)])
    v2 = EVector([EInteger(33),EInteger(66)])

    print "Expected: 264 Output: "+ str(ETimes(v1,v2).eval().value)
    print "Expected: 528 Output: "+ str(ETimes(v1,EPlus(v2,v2)).eval().value)
    print "Expected: 0 Output: "+ str(ETimes(v1,EMinus(v2,v2)).eval().value)

    print "Expected: (102, 103) Output: "+ str(pair(EPlus(v1,EInteger(100)).eval()))
    print "Expected: (102, 103) Output: "+ str(pair(EPlus(EInteger(100),v1).eval()))
    print "Expected: (-98, -97) Output: "+ str(pair(EMinus(v1,EInteger(100)).eval()))
    print "Expected: (98, 97) Output: "+ str(pair(EMinus(EInteger(100),v1).eval()))
    print "Expected: (200, 300) Output: "+ str(pair(ETimes(v1,EInteger(100)).eval()))
    print "Expected: (200, 300) Output: "+ str(pair(ETimes(EInteger(100),v1).eval()))

    print "Expected: (True, False) Output: "+ str(pair(EAnd(EVector([EBoolean(True),EBoolean(False)]),EBoolean(True)).eval()))
    print "Expected: (True, True) Output: "+ str(pair(EOr(EVector([EBoolean(True),EBoolean(False)]),EBoolean(True)).eval()))

    print "VRational Tester >>"
    print "Expected: 1 Output: "+ str(VRational(1,3).numer)
    print "Expected: 3 Output: "+ str(VRational(1,3).denom)
    print "Expected: 2 Output: "+ str(VRational(2,3).numer)
    print "Expected: 3 Output: "+ str(VRational(2,3).denom)

    print "EDiv Tester >>"
    def rat (v): return "{}/{}".format(v.numer,v.denom)
    print "Expected: 1/2 Output: "+ str(rat(EDiv(EInteger(1),EInteger(2)).eval()))
    print "Expected: 2/3 Output: "+ str(rat(EDiv(EInteger(2),EInteger(3)).eval()))
    print "Expected: 1/6 Output: "+ str(rat(EDiv(EDiv(EInteger(2),EInteger(3)),EInteger(4)).eval()))
    print "Expected: 8/3 Output: "+ str(rat(EDiv(EInteger(2),EDiv(EInteger(3),EInteger(4))).eval()))
    print "Expected: 1/2 Output: "+ str(rat(EDiv(EInteger(3),EInteger(6)).eval()))
    print "Expected: 2/3 Output: "+ str(rat(EDiv(EInteger(4),EInteger(6)).eval()))
    print "Expected: -2/3 Output: "+ str(rat(EDiv(EInteger(-4),EInteger(6)).eval()))
    print "Expected: 2/3 Output: "+ str(rat(EDiv(EInteger(-4),EInteger(-6)).eval()))
    print "Expected: <__main__.VInteger object at 0x100f5e590> Output: "+ str(EDiv(EInteger(2),EInteger(1)).eval())
    print "Expected: 2 Output: "+ str(EDiv(EInteger(2),EInteger(1)).eval().value)
    print "Expected: <__main__.VInteger object at 0x100f5e650> Output: "+ str(EDiv(EInteger(4),EInteger(2)).eval())
    print "Expected: 2 Output: "+ str(EDiv(EInteger(4),EInteger(2)).eval().value)


    print "VRational Extension >>"
    half = EDiv(EInteger(1),EInteger(2))
    third = EDiv(EInteger(1),EInteger(3))
    print "Expected: 5/6 Output: "+ str(rat(EPlus(half,third).eval()))
    print "Expected: 3/2 Output: "+ str(rat(EPlus(half,EInteger(1)).eval()))
    print "Expected: 1/6 Output: "+ str(rat(EMinus(half,third).eval()))
    print "Expected: -1/2 Output: "+ str(rat(EMinus(half,EInteger(1)).eval()))
    print "Expected: 1/6 Output: "+ str(rat(ETimes(half,third).eval()))
    print "Expected: 1/2 Output: "+ str(rat(ETimes(half,EInteger(1)).eval()))

    print "VRational Vector Extension >>"
    print "Expected: 5/6 Output: "+ str(rat(EPlus(EVector([half,third]),EVector([third,third])).eval().get(0)))
    print "Expected: 2/3 Output: "+ str(rat(EPlus(EVector([half,third]),EVector([third,third])).eval().get(1)))
    print "Expected: 1/6 Output: "+ str(rat(EMinus(EVector([half,third]),EVector([third,third])).eval().get(0)))
    print "Expected: 1/6 Output: "+ str(rat(EMinus(EVector([half,third]),third).eval().get(0)))
    print "Expected: 1/4 Output: "+ str(rat(ETimes(EVector([half,third]),half).eval().get(0)))
    print "Expected: 1/6 Output: "+ str(rat(ETimes(EVector([half,third]),half).eval().get(1)))

    print "Expected: 1 Output: "+ str(EDiv(EVector([half,third]),EVector([half,third])).eval().get(0).value)
    print "Expected: 1 Output: "+ str(EDiv(EVector([half,third]),EVector([half,third])).eval().get(1).value)
    print "Expected: 1/4 Output: "+ str(rat(EDiv(EVector([half,third]),EInteger(2)).eval().get(0)))
    print "Expected: 1/6 Output: "+ str(rat(EDiv(EVector([half,third]),EInteger(2)).eval().get(1)))