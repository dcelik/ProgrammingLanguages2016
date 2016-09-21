############################################################
# SOLUTIONS TO HOMEWORK 1
#

#
# Expressions
#

class Exp (object):
    def str (self):
        # merely a shortcut
        return str(self)


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
        return add_v(v1,v2)


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
        return sub_v(v1,v2)


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
        return mult_v(v1,v2)


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
            raise Exception("Runtime error: condition in IF should be a Boolean")
        if v.value:
            return self._then.eval()
        else:
            return self._else.eval()


# QUESTION 1(a)

class EIsZero (Exp):

    def __init__ (self,e):
        self._exp = e

    def __str__ (self):
        return "EIsZero({})".format(self._exp)

    def eval (self):
        v = self._exp.eval()
        if v.type != "integer":
            raise Exception("Runtime error: argument to IS-ZERO should be a number")
        return VBoolean(v.value==0)


# QUESTION 1(b,c)

class EAnd (Exp):

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EAnd({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        if v1.type == "boolean" and not v1.value:
            # short circuit
            return VBoolean(False)
        v2 = self._exp2.eval()
        return and_v(v1,v2)

class EOr (Exp):

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EOr({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        if v1.type == "boolean" and v1.value:
            # short circuit
            return VBoolean(True)
        v2 = self._exp2.eval()
        return or_v(v1,v2)


class ENot (Exp):

    def __init__ (self,e):
        self._exp = e

    def __str__ (self):
        return "ENot({})".format(self._exp)

    def eval (self):
        v = self._exp.eval()
        return not_v(v)


class EVector (Exp):

    def __init__ (self,es):
        self._exps = es

    def __str__ (self):
        return "EVector({})".format(self._exps)

    def eval (self):
        vs = [ e.eval() for e in self._exps]
        return VVector(vs)


class EDiv (Exp):

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EDiv({},{})".format(self._exp1,self._exp2)

    def eval (self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        return div_v(v1,v2)


#
# Values
#

class Value (object):
    def str (self):
        # merely a shortcut
        return str(self)
    
    def pr (self):
        print str(self)


class VInteger (Value):
    # Value representation of integers
    def __init__ (self,i):
        self.value = i
        self.type = "integer"

    def __str__ (self):
        return str(self.value)


class VBoolean (Value):
    # Value representation of Booleans
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

    def __str__ (self):
        return str(self.value)


class VVector (Value):
    def __init__ (self,elts):
        self.length = len(elts)
        self._elts = elts
        self.type = "vector"

    def __str__ (self):
        return "< {} >".format(", ".join([ str(v) for v in self._elts]))

    def get (self,n):
        return self._elts[n]


class VRational (Value):
    def __init__ (self,num,den):
        self.numer = num
        self.denom = den
        self.type = "rational"
        if den == 0:
            raise Exception("Runtime error: division by zero in VRational")
        
    def __str__ (self):
        return "{}/{}".format(self.numer,self.denom)

def gcd(a, b):
    while b:
        a, b = b, a%b
    return a

def mk_number (n,d):
    g = gcd(n,d)
    n = n/g
    d = d/g
    if (d==1): 
        return VInteger(n)
    return VRational(n,d)

def is_number (v):
    return v.type in ["integer", "rational"]

def rationalize (v):
    return v if v.type == "rational" else VRational(v.value,1)


# OPERATIONS ON VALUES

def map (f,vec1):
    return [ f(vec1.get(n)) for n in range(0,vec1.length) ]

def lift_v (v,length):
    # creates a vector of length n with the same value v
    return VVector([v] * length)

def map_2 (f,vec1,vec2):
    # applies f to all pairs of values from vec1 and vec2
    # should have vec1 and vec2 of the same length
    return [ f(vec1.get(n),vec2.get(n)) for n in range(0,vec1.length)]

def add_rat (r1,r2):
    # add two rational numbers
    return mk_number(r1.numer * r2.denom + r2.numer * r1.denom,
                     r1.denom * r2.denom)

def sub_rat (r1,r2):
    # subtract two rational numbers
    return mk_number(r1.numer * r2.denom - r2.numer * r1.denom,
                     r1.denom * r2.denom)

def mult_rat (r1,r2):
    # multiply two rational numbers
    return mk_number(r1.numer * r2.numer, r1.denom * r2.denom)

def div_rat (r1,r2):
    # multiply two rational numbers
    return mk_number(r1.numer * r2.denom, r1.denom * r2.numer)


def add_v (v1,v2):
    if is_number(v1) and is_number(v2):
        return add_rat(rationalize(v1),rationalize(v2))
    if v1.type == "vector" and v2.type == "vector" and v1.length == v2.length:
        return VVector(map_2(add_v,v1,v2))
    if v1.type == "vector" and is_number(v2):
        return add_v(v1,lift_v(v2,v1.length))
    if is_number(v1) and v2.type == "vector":
        return add_v(lift_v(v1,v2.length),v2)
    raise Exception("Runtime error: wrong types for PLUS ({} and {})".format(v1.type,v2.type))

def sub_v (v1,v2):
    if is_number(v1) and is_number(v2):
        return sub_rat(rationalize(v1),rationalize(v2))
    if v1.type == "vector" and v2.type == "vector" and v1.length == v2.length:
        return VVector(map_2(sub_v,v1,v2))
    if v1.type == "vector" and is_number(v2):
        return sub_v(v1,lift_v(v2,v1.length))
    if is_number(v1) and v2.type == "vector":
        return sub_v(lift_v(v1,v2.length),v2)
    raise Exception("Runtime error: wrong types for MINUS ({} and {})".format(v1.type,v2.type))

def sum_list_v (lst):
    result = VInteger(0)
    for v in lst:
        result = add_v(result,v)
    return result

def mult_v (v1,v2):
    if is_number(v1) and is_number(v2):
        return mult_rat(rationalize(v1),rationalize(v2))
    if v1.type == "vector" and v2.type == "vector" and v1.length == v2.length:
        return sum_list_v(map_2(mult_v,v1,v2))
    if v1.type == "vector" and is_number(v2):
        return VVector(map_2(mult_v,v1,lift_v(v2,v1.length)))
    if is_number(v1) and v2.type == "vector":
        return VVector(map_2(mult_v,lift_v(v1,v2.length),v2))
    raise Exception("Runtime error: wrong types for TIMES ({} and {})".format(v1.type,v2.type))

def div_v (v1,v2):
    if is_number(v1) and is_number(v2):
        return div_rat(rationalize(v1),rationalize(v2))
    if v1.type == "vector" and v2.type == "vector" and v1.length == v2.length:
        return VVector(map_2(div_v,v1,v2))
    if v1.type == "vector" and is_number(v2):
        return div_v(v1,lift_v(v2,v1.length))
    if is_number(v1) and v2.type == "vector":
        return div_v(lift_v(v1,v2.length),v2)
    raise Exception("Runtime error: wrong types for DIV ({} and {})".format(v1.type,v2.type))


def and_v (v1,v2):
    if v1.type == "boolean" and v2.type == "boolean":
        return VBoolean(v1.value and v2.value)
    if v1.type == "vector" and v2.type == "vector" and v1.length == v2.length:
        return VVector(map_2(and_v,v1,v2))
    if v1.type == "vector" and v2.type == "boolean":
        return and_v(v1,lift_v(v2,v1.length))
    if v1.type == "boolean" and v2.type == "vector":
        return and_v(lift_v(v1,v2.length),v2)
    raise Exception("Runtime error: wrong types for AND ({} and {})".format(v1.type,v2.type))

def or_v (v1,v2):
    if v1.type == "boolean" and v2.type == "boolean":
        return VBoolean(v1.value or v2.value)
    if v1.type == "vector" and v2.type == "vector" and v1.length == v2.length:
        return VVector(map_2(or_v,v1,v2))
    if v1.type == "vector" and v2.type == "boolean":
        return or_v(v1,lift_v(v2,v1.length))
    if v1.type == "boolean" and v2.type == "vector":
        return or_v(lift_v(v1,v2.length),v2)
    raise Exception("Runtime error: wrong types for OR ({} and {})".format(v1.type,v2.type))

def not_v (v1):
    if v1.type == "boolean":
        return VBoolean(not v1.value)
    if v1.type == "vector":
        return VVector(map(not_v,v1))
    raise Exception("Runtime error: wrong type for NOT ({})".format(v1.type))
    



# helper function 

def evp (e):
    # eval and print
    print (e.eval())
    