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

    FILE *fp = fopen("\x0a", "w");
    fwrite("\x00\x00\x00\x00", 4, 1, fp);
    fclose(fp);

    if(fork() == 0) {
        dup2(pipe1[0], 0);
        close(pipe1[0]);
        close(pipe1[1]);

        dup2(pipe2[0], 2);
        close(pipe2[0]);
        close(pipe2[1]);

        execve("/home/input/input", argv, envp);
    }
    else {
        write(pipe1[1], "\x00\x0a\x00\xff", 4);
        write(pipe2[1], "\x00\x0a\x02\xff", 4);

        sleep(5);
        struct sockaddr_in servaddr;
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        memset(&servaddr, 0, sizeof(servaddr));
        servaddr.sin_family = AF_INET;
        servaddr.sin_port = htons(atoi(argv['C']));
        servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");
        connect(sock, (struct sockaddr *)&servaddr, sizeof(servaddr));
        send(sock, "\xde\xad\xbe\xef", 4, 0);
        close(sock);

        int stat;
        wait(&stat);
        unlink("\x0a");
        return 0;
    }
}