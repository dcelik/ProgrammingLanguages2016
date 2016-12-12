#include <stdlib.h>

 typedef struct tClosure{
    int val;
    void* addr;
    int isInt;
    int envLen;
    struct tClosure *p_env;
} tClosure;

void* addr;

//RESULT
tClosure result;
//ARGS
tClosure args[2];
int args_index = 0;
//ENV
tClosure* env;
int env_index = 0;

//int n = 10;

int oper_plus(tClosure clo[]){
    return clo[0].val+clo[1].val;
}
int oper_minus(tClosure clo[]){
    return clo[0].val-clo[1].val;
}
int oper_times(tClosure clo[]){
    return clo[0].val*clo[1].val;
}
int oper_zero(tClosure clo[]){
    //true->1
    //false->0
    return clo[0].val==0;
}

int main(){
    //Setup result
    result.val = -1;
    result.isInt = 0;
    result.envLen = 0;
    result.p_env = (tClosure *)malloc(sizeof(tClosure)*result.envLen);
    env = (tClosure *)malloc(sizeof(tClosure)*0);
    tClosure* temp_env = (tClosure *)malloc(sizeof(tClosure)*0);
    result.val = 10;
    result.isInt = 1;
    args[args_index] = result;
    args_index++;
    result.val = 0;
    result.isInt = 1;
    args[args_index] = result;
    args_index++;
    addr = &&PL_8;
    PL_8:
    result.addr = addr;
    result.envLen = sizeof(env)/sizeof(tClosure);
    result.p_env = env;
    temp_env = realloc(env,sizeof(env)+sizeof(result));
    env = temp_env;
    env[env_index]=result;
    env_index++;
    temp_env = realloc(env,sizeof(env)+sizeof(args));
    env = temp_env;
    if(args_index>=1){
        env[env_index]=args[0];
        env_index++;
    }
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }
    args_index = 0;
    result = env[1];
    args[args_index] = result;
    args_index++;
    result.val = oper_zero(args);
    result.isInt = 1;
    addr = &&PL_55;
    if(result.val==1){
        goto *addr;
    }
    args_index = 0;
    result = env[1];
    args[args_index] = result;
    args_index++;
    result.val = 1;
    result.isInt = 1;
    args[args_index] = result;
    args_index++;
    result.val = oper_minus(args);
    result.isInt = 1;
    args_index = 0;
    args[args_index] = result;
    args_index++;
    temp_env = realloc(env,sizeof(env)+sizeof(args));
    env = temp_env;
    if(args_index>=1){
        env[env_index]=args[0];
        env_index++;
    }
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }
    args_index = 0;
    result = env[1];
    args[args_index] = result;
    args_index++;
    result = env[2];
    args[args_index] = result;
    args_index++;
    result.val = oper_plus(args);
    result.isInt = 1;
    args_index = 0;
    args[args_index] = result;
    args_index++;
    temp_env = realloc(env,sizeof(env)+sizeof(args));
    env = temp_env;
    if(args_index>=1){
        env[env_index]=args[0];
        env_index++;
    }
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }
    args_index = 0;
    result = env[3];
    args[args_index] = result;
    args_index++;
    result = env[4];
    args[args_index] = result;
    args_index++;
    result = env[0];
    addr = result.addr;
    env = realloc(result.p_env,sizeof(tClosure)*result.envLen);
    goto *addr;
    PL_55:
    result = env[2];
    return result.val;
}
