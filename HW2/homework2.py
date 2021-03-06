############################################################
# HOMEWORK 2
#
# Team members: Deniz Celik & Jacob Riedel
#
# Emails: deniz.celik@students.olin.edu
#         jacob.riedel@students.olin.edu
#
# Remarks:
#   For Q2, we were confused if we implemented it correctly, as 
#    it seemed to simple to just evaluate e1 before substituting.
#   For Q1a (ELetS), we did not implement it purely recursively,
#    instead we reduced our bindings down through substitution before
#    creating returning a new ELet and calling eval on that.
#    We found this approach to be more intuitive for us but would have
#    implemented the recursive substitution version if time had allowed.
#   Thanks!



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

    def eval (self,prim_dict,func_dict):
        return VInteger(self._integer)

    def substitute (self,id,new_e):
        return self


class EBoolean (Exp):
    # Boolean literal

    def __init__ (self,b):
        self._boolean = b

    def __str__ (self):
        return "EBoolean({})".format(self._boolean)

    def eval (self,prim_dict,func_dict):
        return VBoolean(self._boolean)

    def substitute (self,id,new_e):
        return self


class EPrimCall (Exp):

    def __init__ (self,name,es):
        self._name = name
        self._exps = es

    def __str__ (self):
        return "EPrimCall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self,prim_dict,func_dict):
        vs = [ e.eval(prim_dict,func_dict) for e in self._exps ]
        return apply(prim_dict[self._name],vs)

    def substitute (self,id,new_e):
        new_es = [ e.substitute(id,new_e) for e in self._exps]
        return EPrimCall(self._name,new_es)


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,prim_dict,func_dict):
        v = self._cond.eval(prim_dict,func_dict)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(prim_dict,func_dict)
        else:
            return self._else.eval(prim_dict,func_dict)

    def substitute (self,id,new_e):
        return EIf(self._cond.substitute(id,new_e),
                   self._then.substitute(id,new_e),
                   self._else.substitute(id,new_e))


class ELet (Exp):
    # local binding

    def __init__ (self,bindings,e1):
        self._bindings = bindings
        self._e1 = e1

    def __str__ (self):
        return "ELet({},{})".format(self._bindings,self._e1)

    def eval (self,prim_dict,func_dict):
        new_e1 = self._e1
        for bind in self._bindings:
            new_e1 = new_e1.substitute(bind[0],bind[1])
        return new_e1.eval(prim_dict,func_dict)

    def substitute (self,id,new_e):
        if id in [ids[0] for ids in self._bindings]:
            return ELet(\
                [(newb[0],newb[1].substitute(id,new_e)) for newb in self._bindings],\
                self._e1)
        return ELet(\
                [(newb[0],newb[1].substitute(id,new_e)) for newb in self._bindings],\
                self._e1.substitute(id,new_e))



class ELetS (ELet):
    # local binding

    def __str__ (self):
        return "ELetS({},{})".format(self._bindings,self._e1)

    def eval (self,prim_dict,func_dict):
        final_binds = []
        for index in range(len(self._bindings)):
            bind = self._bindings[index]
            if range(len(self._bindings[index+1:]))==[]:
                final_binds.append(bind)
            for j in range(index+1,index+1+len(self._bindings[index+1:])):
                if self._bindings[j][0]==bind[0]:
                    break
                self._bindings[j] = (self._bindings[j][0],self._bindings[j][1].substitute(bind[0],bind[1]))
                if len(self._bindings[index+1:])==1:
                    final_binds.append(bind)
        return ELet(final_binds,self._e1).eval(prim_dict,func_dict)

    def substitute (self,id,new_e):
        for index in range(len(self._bindings)):
            if self._bindings[index][0]==id:
                break
            self._bindings[index] = (self._bindings[index][0],self._bindings[index][1].substitute(id,new_e))
        return ELetS(self._bindings,self._e1)

class ELetV (Exp):
    # local binding

    def __init__ (self,id,e1,e2):
        self._id = id
        self._e1 = e1
        self._e2 = e2

    def __str__ (self):
        return "ELet({},{},{})".format(self._id,self._e1,self._e2)

    def eval (self,prim_dict,func_dict):
        val = self._e1.eval(prim_dict,func_dict)
        if val.type=='integer':
            new_exp = EInteger(val.value)
            new_e2 = self._e2.substitute(self._id,new_exp)
        if val.type=='boolean':
            new_exp = EBoolean(val.value)
            new_e2 = self._e2.substitute(self._id,new_exp)
        return new_e2.eval(prim_dict,func_dict)

    def substitute (self,id,new_e):
        if id == self._id:
            return ELetV(self._id,
                        self._e1.substitute(id,new_e),
                        self._e2)
        return ELetV(self._id,
                    self._e1.substitute(id,new_e),
                    self._e2.substitute(id,new_e))

class ECall (EPrimCall):
    # call a user function

    def __str__ (self):
        return "ECall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self,prim_dict,fun_dict):
        func = fun_dict[self._name]
        new_e = func['body']
        params = func['params']
        for index in xrange(len(params)):
            new_e = new_e.substitute(params[index],self._exps[index])
        return new_e.eval(prim_dict,fun_dict)

    def substitute (self,id,new_e):
        new_es = [e.substitute(id,new_e) for e in self._exps]
        return ECall(self._name,new_es)

class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,prim_dict,func_dict):
        raise Exception("Runtime error: unknown identifier {}".format(self._id))

    def substitute (self,id,new_e):
        if id == self._id:
            return new_e
        return self

class EValue (Exp):
    # Value as Expression

    def __init__ (self,val):
        self._value = val

    def __str__ (self):
        return "EValue({})".format(self._value)

    def eval (self,prim_dict,func_dict):
        return self._value

    def substitute (self,id,new_e):
        return self


    
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





# Primitive operations

def oper_plus (v1,v2): 
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_zero (v1):
    if v1.type == "integer":
        return VBoolean(v1.value==0)
    raise Exception ("Runtime error: type error in zero?")
# Initial primitives dictionary

INITIAL_PRIM_DICT = {
    "+": oper_plus,
    "*": oper_times,
    "-": oper_minus,
    "zero?": oper_zero
}

def testIf(val,expression):
    tval = (val==expression)
    if tval:
        print tval
    else:
        print "Expected: " + str(val) + " Got: " + str(expression)

if __name__ == '__main__':


    FUN_DICT = {
      "square": {"params":["x"],
                 "body":EPrimCall("*",[EId("x"),EId("x")])},
      "=": {"params":["x","y"],
            "body":EPrimCall("zero?",[EPrimCall("-",[EId("x"),EId("y")])])},
      "+1": {"params":["x"],
             "body":EPrimCall("+",[EId("x"),EValue(VInteger(1))])},
      "sum_from_to": {"params":["s","e"],
                      "body":EIf(ECall("=",[EId("s"),EId("e")]),
                                 EId("s"),
                                 EPrimCall("+",[EId("s"),
                                                ECall("sum_from_to",[ECall("+1",[EId("s")]),
                                                                     EId("e")])]))}
        }

    print("Q1a Testers")
    try:
        testIf(99,ELet([("a",EInteger(99))],EId("a")).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(99,ELet([("a",EInteger(99)),
              ("b",EInteger(66))],EId("a")).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(66,ELet([("a",EInteger(99)),
              ("b",EInteger(66))],EId("b")).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(66,ELet([("a",EInteger(99))],
             ELet([("a",EInteger(66)),
                   ("b",EId("a"))],
                  EId("a"))).eval(INITIAL_PRIM_DICT,FUN_DICT).value) 

        testIf(99,ELet([("a",EInteger(99))],
             ELet([("a",EInteger(66)),
                   ("b",EId("a"))],
                  EId("b"))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(15,ELet([("a",EInteger(5)),
              ("b",EInteger(20))],
             ELet([("a",EId("b")),
                   ("b",EId("a"))],
                  EPrimCall("-",[EId("a"),EId("b")]))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(5,ELet([("e",EInteger(5))],ELet([("a",EInteger(6))],EId('e'))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)
    except Exception as e:
        print e

    print("Q1b Testers")
    try:
        testIf(99,ELetS([("a",EInteger(99))],EId("a")).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(99,ELetS([("a",EInteger(99)),
           ("b",EInteger(66))],EId("a")).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(66,ELetS([("a",EInteger(99)),
           ("b",EInteger(66))],EId("b")).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(0,ELetS([('b',EInteger(10)),('a',EId('b')),('b',EId('a'))],EPrimCall("-",[EId("a"),EId("b")])).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(66,ELet([("a",EInteger(99))],
         ELetS([("a",EInteger(66)),
                ("b",EId("a"))],
               EId("a"))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(66,ELet([("a",EInteger(99))],
         ELetS([("a",EInteger(66)),
                ("b",EId("a"))],
               EId("b"))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(0,ELetS([("a",EInteger(5)),
           ("b",EInteger(20))],
          ELetS([("a",EId("b")),
                 ("b",EId("a"))],
                EPrimCall("-",[EId("a"),EId("b")]))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)
    except Exception as e:
        print e

    print("Q2a Testers")
    try:
        testIf(10,ELetV("a",EInteger(10),EId("a")).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(10,ELetV("a",EInteger(10),
          ELetV("b",EInteger(20),EId("a"))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(20,ELetV("a",EInteger(10),
          ELetV("a",EInteger(20),EId("a"))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(30,ELetV("a",EPrimCall("+",[EInteger(10),EInteger(20)]),
          ELetV("b",EInteger(20),EId("a"))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(900,ELetV("a",EPrimCall("+",[EInteger(10),EInteger(20)]),
          ELetV("b",EInteger(20),
                EPrimCall("*",[EId("a"),EId("a")]))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(60,ELetV("a",EPrimCall("+",[EInteger(10),EInteger(20)]),
            ELetV("b",EPrimCall("*",[EInteger(10),EInteger(20)]),
                ELetV("b",EId("a"),
                    EPrimCall("+",[EId("a"),EId("b")])))).eval(INITIAL_PRIM_DICT,FUN_DICT).value)
    except Exception as e:
        print e

    print("Q3 Testers")
    try:
        testIf(101,ECall("+1",
          [EInteger(100)]).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(301,ECall("+1",
          [EPrimCall("+",[EInteger(100),EInteger(200)])]).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(102,ECall("+1",
          [ECall("+1",
                 [EInteger(100)])]).eval(INITIAL_PRIM_DICT,FUN_DICT).value)
        testIf(False,ECall("=",[EInteger(1),EInteger(2)]).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(True,ECall("=",[EInteger(1),EInteger(1)]).eval(INITIAL_PRIM_DICT,FUN_DICT).value)

        testIf(55,ECall("sum_from_to",[EInteger(0),EInteger(10)]).eval(INITIAL_PRIM_DICT,FUN_DICT).value)
    except Exception as e:
        print e