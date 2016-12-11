#######################################################################################
####################################### Code_C ########################################
#######################################################################################
#       RETURN:
#             return result.val;
#
#       LOAD:
#       n:
#             result.val = n;
#             result.isInt = 1;
#
#       LOAD-ADDR:
#       label:
#             addr = &&label;
#
#       LOOKUP:
#       env-index:
#             result = env[env-index];
#
#       CLEAR-ARGS:
#             args_index = 0;
#
#       PUSH-ARGS:
#             args[args_index] = result;
#             args_index++;
#
#       PRIM-CALL:
#       oper:
#             result.val = oper(args);
#             result.isInt = 1;
#
#       PUSH-ENV:
#             tClosure* temp_env = realloc(env,sizeof(env)+sizeof(result));
#             env = temp_env;
#             env[env_index]=result;
#             env_index++;
#
#       PUSH-ENV-ARGS:
#             temp_env = realloc(env,sizeof(env)+sizeof(args));
#             env = temp_env;
#             if(args_index>=1){
#                   env[env_index]=args[0];
#                   env_index++;
#             }
#             if(args_index==2){
#                   env[env_index]=args[1];
#                   env_index++;
#             }
#     
#       JUMP:
#             goto addr;
#
#       JUMP-TRUE:
#             if(result.val==1){
#                   goto addr;
#             }
#
#       LOAD-FUN:
#             result.addr = addr;
#             result.envLen = sizeof(env)/sizeof(tClosure);
#             result.p_env = env;
#
#       LOAD-ADDR-ENV:
#             addr = result.addr;
#             env = (tClosure *)malloc(sizeof(tClosure)*result.envLen);
#             env = result.p_env;
#
#######################################################################################
#######################################################################################

code = ["LOAD",
        10,
        "PUSH-ARGS",
        "LOAD",
        0,
        "PUSH-ARGS",
        "LOAD-ADDR",
        "PL_8",   #loop
        "PL_8:",
        "LOAD-FUN",  #loop
        "PUSH-ENV",
        "PUSH-ENV-ARGS",
        "CLEAR-ARGS",
        "LOOKUP",
        1,
        "PUSH-ARGS",
        "PRIM-CALL",
        "oper_zero",
        "LOAD-ADDR",
        "PL_55", #done
        "JUMP-TRUE",
        "CLEAR-ARGS",
        "LOOKUP",
        1,
        "PUSH-ARGS",
        "LOAD",
        1,
        "PUSH-ARGS",
        "PRIM-CALL",
        "oper_minus",
        "CLEAR-ARGS",
        "PUSH-ARGS",
        "PUSH-ENV-ARGS",
        "CLEAR-ARGS",
        "LOOKUP",
        1,
        "PUSH-ARGS",
        "LOOKUP",
        2,
        "PUSH-ARGS",
        "PRIM-CALL",
        "oper_plus",
        "CLEAR-ARGS",
        "PUSH-ARGS",
        "PUSH-ENV-ARGS",
        "CLEAR-ARGS",
        "LOOKUP",
        3,
        "PUSH-ARGS",
        "LOOKUP",
        4,
        "PUSH-ARGS",
        "LOOKUP",
        0,
        "LOAD-ADDR-ENV",
        "JUMP",
        "PL_55:",  
        "LOOKUP",   #done
        2,
        "RETURN"]

def translate_into_c(code):
    pc = 0
    while True:

        op = code[pc]

        if op == "RETURN":
            print "return result.val;\n"
            pc += 1
            break

        elif op == "CLEAR-ARGS":
            print"args_index = 0;\n"
            pc+=1

        elif op == "LOAD":
            print "result.val = {};\nresult.isInt = 1;\n".format(code[pc+1])
            pc += 2
                  
        elif op == "PUSH-ARGS":
            print "args[args_index] = result;\nargs_index++;\n"
            pc += 1

        elif op == "LOOKUP":
            print "result = env[{}]\n".format(code[pc+1])
            pc += 2

        elif op == "LOAD-ADDR-ENV":
            print "addr = result.addr;\nenv = (tClosure *)malloc(sizeof(tClosure)*result.envLen);\nenv = result.p_env;\n"
            pc += 1

        elif op == "JUMP":
            print "goto addr;\n"
            pc += 1
                  
        elif op == "PUSH-ENV-ARGS":
            print "temp_env = realloc(env,sizeof(env)+sizeof(args));\nenv = temp_env;\nif(args_index>=1){\n    env[env_index]=args[0];\n    env_index++;\n}\nif(args_index==2){\n    env[env_index]=args[1];\n    env_index++;\n}\n"
            pc += 1
          
        elif op == "PUSH-ENV":
            print "tClosure* temp_env = realloc(env,sizeof(env)+sizeof(result));\nenv = temp_env;\nenv[env_index]=result;\nenv_index++;\n"
            pc += 1

        elif op == "LOAD-ADDR":
            print "addr = &&{}\n".format(code[pc+1])
            pc += 2

        elif op == "LOAD-FUN":
            print "result.addr = addr;\nresult.envLen = sizeof(env)/sizeof(tClosure);\nresult.p_env = env;\n"
            pc += 1

        elif op == "PRIM-CALL":
            print "result.val = {}(args);\nresult.isInt = 1;\n".format(code[pc+1])
                  # print [ str(a) for a in args ]
            pc += 2

        elif op == "JUMP-TRUE":
            print "if(result.val==1){\n    goto addr;\n}\n"
            pc += 1

        elif op[:2] == "PL":
            print "{}\n".format(op)
            pc += 1
        else:
            raise Exception("Unrecognized opcode: {}".format(op))


translate_into_c(code)


