#include <stdlib.h>
#include <stdio.h>

 typedef struct tClosure{
    int val;
    void* addr;
    int isInt;
    int envLen;
    struct tClosure* p_env;
} tClosure;

void* addr;

//RESULT
tClosure result;
//ARGS
tClosure args[2];
int args_index = 0;
//ENV
tClosure env[1024];
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
    result.envLen = 1;
    result.p_env = malloc(sizeof(tClosure)*result.envLen);

    result.val = 10;
    result.isInt = 1;
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    result.val = 0;
    result.isInt = 1;
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    addr = &&PL_8;
    PL_8:
    result.addr = addr;
    *result.p_env = env;
    env[env_index]=result;
    env_index++;
    if(args_index>=1){
        env[env_index]=args[0];
        printf("Saving to ENV: %d\n", env[env_index].val);
        env_index++;
    }
    if(args_index==2){
        env[env_index]=args[1];
        printf("Saving to ENV: %d\n", env[env_index].val);
        env_index++;
    }
    args_index = 0;
    result = env[1];
    printf("Loading from ENV: %d\n", env[1].val);
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    result.val = oper_zero(args);
    printf("oper_zero\n");
    result.isInt = 1;
    addr = &&PL_55;
    if(result.val==1){
        goto *addr;
    }
    args_index = 0;
    result = env[1];
    printf("Loading from ENV: %d\n", env[1].val);
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    result.val = 1;
    result.isInt = 1;
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    result.val = oper_minus(args);
    printf("oper_minus\n");
    result.isInt = 1;
    args_index = 0;
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    if(args_index>=1){
        env[env_index]=args[0];
        printf("Saving to ENV: %d\n", env[env_index].val);
        env_index++;
    }
    if(args_index==2){
        env[env_index]=args[1];
        printf("Saving to ENV: %d\n", env[env_index].val);
        env_index++;
    }
    args_index = 0;
    result = env[1];
    printf("Loading from ENV: %d\n", env[1].val);
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    result = env[2];
    printf("Loading from ENV: %d\n", env[2].val);
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    result.val = oper_plus(args);
    printf("oper_plus\n");
    result.isInt = 1;
    args_index = 0;
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    if(args_index>=1){
        env[env_index]=args[0];
        printf("Saving to ENV: %d\n", env[env_index].val);
        env_index++;
    }
    if(args_index==2){
        env[env_index]=args[1];
        printf("Saving to ENV: %d\n", env[env_index].val);
        env_index++;
    }
    args_index = 0;
    result = env[3];
    printf("Loading from ENV: %d\n", env[3].val);
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    result = env[4];
    printf("Loading from ENV: %d\n", env[4].val);
    args[args_index] = result;
    printf("ARGS: %d\n", args[args_index].val);
    args_index++;
    result = env[0];
    printf("Loading from ENV: %d\n", env[0].val);
    addr = result.addr;
    ///////*****ERROR in LOADING ENV from RESULT.ENV*****/////////
    // Issues caused by null result environment from LOAD-FUN command.
    // Result.p_env cannot be empty. Result.envLen should be >= 1

    env = result.p_env;
    goto *addr;
    PL_55:
    result = env[2];
    return result.val;
}
