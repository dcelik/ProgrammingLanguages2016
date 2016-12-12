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
tClosure args[16];
int args_index = 0;
//ENV
tClosure env[16];
int env_index = 0;

int i;

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

    result.val = 200000;

    args[args_index] = result;
    args_index++;

    result.val = 0;

    args[args_index] = result;
    args_index++;

    addr = &&PL_8;

    PL_8:

    result.addr = addr;
    *result.p_env = env;
    result.envLen = env_index;

    env[env_index]=result;
    env_index++;

    for (i=0;i<=args_index-1;i++){
        env[env_index] = args[i];
        env_index++;
    }

    args_index = 0;

    result = env[1];

    args[args_index] = result;
    args_index++;

    result.val = oper_zero(args);

    addr = &&PL_55;

    if(result.val==1){
        goto *addr;
    }

    args_index = 0;

    result = env[1];

    args[args_index] = result;
    args_index++;

    result.val = 1;

    args[args_index] = result;
    args_index++;

    result.val = oper_minus(args);

    args_index = 0;

    args[args_index] = result;
    args_index++;

    for (i=0;i<=args_index-1;i++){
        env[env_index] = args[i];
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

    args_index = 0;

    args[args_index] = result;
    args_index++;

    for (i=0;i<=args_index-1;i++){
        env[env_index] = args[i];
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
    *env = **result.p_env;
    env_index = result.envLen;

    goto *addr;

    PL_55:

    result = env[2];

    return result.val;
}

int main(){
    printf("Answer: %lli",func());
    return 0;
}
