#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
int main(int argc, char const *argv[])
{
	char fname[128];
	unsigned long long otp[2];

	int fd = open("/dev/urandom", O_RDONLY);
	if(fd==-1) exit(-1);

	if(read(fd, otp, 16)!=16) exit(-1);
	close(fd);

	sprintf(fname, "%llu--%llu", otp[0], otp[1]);
	printf("%s\n", fname);
	return 0;
}