#include <stdio.h>
int main()
{
	int fd;
	fd = open("/dev/zero", 0, 1, 3);
	if (fd < 0)
	{
		printf("fd < 0\n");
		return 0;
	}
	char buff[3] = "ab";
	int ret = read(fd, &buff[2], 1);
	
	printf("ret = %d, value = %s\n", ret, buff);

	return 0;
}