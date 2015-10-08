#include "stdio.h"
int main()
{
	int size;
	scanf("%d", &size);
	printf("size:%d\n", size);
	char buff[32];
	int i;
	char tmp_buff;

	if (size > 10)
		size = 10;

	/*
	printf("before:\n");
	for (i = 0; i < size; ++i)
	{
		printf("%02x ", buff[i]&0xff);
	}
	*/

	for (i = 0; i < size; i++)
	{
		read(0, &tmp_buff, 1);
		printf("%02x\n", tmp_buff);
		if (tmp_buff == '\n')
			break;
		buff[i] = tmp_buff;
	}
	printf("\n");
	printf("i:%d\n", i);

	/*
	printf("after:\n");
	for (i = 0; i < size; ++i)
	{
		printf("%02x ", buff[i]&0xff);
	}

	printf("\n");
	printf("end\n");
	*/

	return 0;
}