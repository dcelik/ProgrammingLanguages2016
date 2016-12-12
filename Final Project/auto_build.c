#include <stdlib.h>

 typedef struct tClosure{
    long long val;
    void* addr;
    int envLen;
    struct tClosure * p_env[16];
} tClosure;

void* addr;

//RESULT
tClosure result;
//ARGS
tClosure args[2];
int args_index = 0;
//ENV
tClosure env[16];
int env_index = 0;


long long oper_plus(tClosure clo[]){
    return clo[0].val+clo[1].val;
}
long long oper_minus(tClosure clo[]){
    return clo[0].val-clo[1].val;
}
long long oper_times(tClosure clo[]){
    return clo[0].val*clo[1].val;
}
long long oper_zero(tClosure clo[]){
    //true->1
    //false->0
    return clo[0].val==0;
}

long long func(){
    //Setup result
    result.val = -1;
    result.envLen = 0;

    env[env_index]=args[0];                   
    env_index++;                   
    if(args_index==2){                   
        env[env_index]=args[1];                   
        env_index++;                   
    }

    args_index = 0;

    result = env[0];

    args[args_index] = result;
    args_index++;

    result = env[1];

    args[args_index] = result;
    args_index++;

    result.val = oper_plus(args);

    args_index = 0;

    args[args_index] = result;
    args_index++;

    result = env[2];

    addr = result.addr;                   
    *env = **result.p_env;                   
    env_index = result.envLen;

    goto *addr;

    env[env_index]=args[0];                   
    env_index++;                   
    if(args_index==2){                   
        env[env_index]=args[1];                   
        env_index++;                   
    }

    args_index = 0;

    result = env[0];

    args[args_index] = result;
    args_index++;

    result = env[1];

    args[args_index] = result;
    args_index++;

    result.val = oper_minus(args);

    args_index = 0;

    args[args_index] = result;
    args_index++;

    result = env[2];

    addr = result.addr;                   
    *env = **result.p_env;                   
    env_index = result.envLen;

    goto *addr;

    env[env_index]=args[0];                   
    env_index++;                   
    if(args_index==2){                   
        env[env_index]=args[1];                   
        env_index++;                   
    }

    args_index = 0;

    result = env[0];

    args[args_index] = result;
    args_index++;

    result.val = oper_zero(args);

    args_index = 0;

    args[args_index] = result;
    args_index++;

    result = env[1];

    addr = result.addr;                   
    *env = **result.p_env;                   
    env_index = result.envLen;

    goto *addr;

    env[env_index]=args[0];                   
    env_index++;                   
    if(args_index==2){                   
        env[env_index]=args[1];                   
        env_index++;                   
    }

    result = env[0];

    return result.val;
}

int main(){
    printf("Answer: %lli",func());
    return 0;
}
