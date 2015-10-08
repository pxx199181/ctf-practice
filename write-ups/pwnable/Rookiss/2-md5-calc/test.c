#include<stdio.h>
#include<time.h>
#include<string.h>
int main(int argc, char** argv)
{
	int offset = 0;
	int count = 0;
	if (argc > 2) 
	{
		offset = atoi(argv[1]);
		count = atoi(argv[2]);
		//printf("offset:%d\n", offset);
		//printf("count:%d\n", count);
	}
	else
	{
		printf("usage:./main offset count\n");
	}
	int number = time(0) - offset;
	//printf("%d\n", number);
	srand(number);
	int i;
	for (i = 0; i < count; i++)
		printf("%d ", rand());
	return 0;
}