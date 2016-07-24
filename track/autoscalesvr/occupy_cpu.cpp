#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

static void* thread_start(void* args)
{
    int i = 1;
    while(1)
        i = i*2+65535;

    if (i%2==0)
        return (void*)0;
    else
        return (void*)1;
}

int main(int argc, char* argv[])
{
    if (argc < 2)
    {
        printf("usage: %s threads_num", argv[0]);
        return -1;
    }
    int threads_num = atoi(argv[1]);
    if (threads_num < 1 || threads_num > 1000)
    {
        printf("usage: %s threads_num", argv[0]);
        return -1;
    }

    for (int i = 0; i < threads_num; i++)
    {
        pthread_t thread_id;
        int ret = pthread_create(&thread_id, NULL, &thread_start, NULL);
    }

    while(1)
        sleep(1);

    return 0;
}
